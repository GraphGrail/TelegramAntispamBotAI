import os
import telebot
import sqlite3
import settings
from datetime import datetime
from comment_evaluator import CommentEvaluator

#spacy.load('xx_ent_wiki_sm')
script_dir = os.path.dirname(__file__)

bot = telebot.TeleBot(settings.BOT_TOKEN)
conn = sqlite3.connect(os.path.join(script_dir, 'antispambot.db'), check_same_thread=False)
c = conn.cursor()

evaluator = CommentEvaluator()


def get_language(lang_code):
    if not lang_code:
        return "en"
    if "-" in lang_code:
        lang_code = lang_code.split("-")[0]
    if lang_code == "ru":
        return "ru"
    else:
        return "en"


@bot.message_handler(func=lambda message: message.text and evaluator.analyze(message.text) == "spam")
def handle_spam(message):
    if int(message.from_user.id) in settings.ADMINS:
        c.execute('SELECT ID FROM userstat WHERE user_id=?', (message.from_user.id,))
        rows = c.fetchall()
        if len(rows) == 0:
            c.execute('INSERT INTO userstat VALUES(NULL, ?, ?)', (message.from_user.id, 1,))
            c.execute('INSERT INTO spam VALUES(NULL, ?, ?, ?, ?, ?)', (message.from_user.id, message.chat.id,
                                                                          message.message_id,
                                                                          message.text,
                                                                          datetime.now(),))
            conn.commit()
        else:
            c.execute('UPDATE userstat SET spam_count=spam_count+1')
            c.execute('INSERT INTO spam VALUES(NULL, ?, ?, ?, ?, ?)', (message.from_user.id, message.chat.id,
                                                                          message.message_id,
                                                                          message.text,
                                                                          datetime.now(),))
            conn.commit()
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id,
                         message.from_user.first_name + settings.strings.get(get_language(message.from_user.language_code)).get("spam_msg"))


if __name__ == "__main__":
    bot.polling(none_stop=True)
