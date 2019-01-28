import os
import re
from emoji import UNICODE_EMOJI
import spacy
from spacy.matcher import Matcher
import pymorphy2


class CommentEvaluator():
    def __init__(self):

        self.nlp_ = spacy.load('xx_ent_wiki_sm')
        self.morph_ = pymorphy2.MorphAnalyzer()

        self.spamPatterns_ = []

        #russian - advert
        self.spamPatterns_.append([{"LOWER": "москва_сити"}])

        #russian - motivation phrases
        self.spamPatterns_.append([{"LOWER": "присоединяться"}, {"OP": "+"}, {"LOWER": "сейчас"}])
        self.spamPatterns_.append([{"LOWER": "присоединять"}, {"OP": "+"}, {"LOWER": "сейчас"}])
        self.spamPatterns_.append([{"LOWER": "подписываться"}, {"OP": "+"}, {"LOWER": "нас"}])
        self.spamPatterns_.append([{"LOWER": "подписаться"}, {"OP": "+"}, {"LOWER": "нас"}])
        self.spamPatterns_.append([{"LOWER": "присоединяться"}, {"OP": "+"}, {"LOWER": "к"}, {"OP": "+"}, {"LOWER": "команда"}])
        self.spamPatterns_.append([{"LOWER": "огромный"}, {"OP": "+"}, {"LOWER": "профит"}])
        self.spamPatterns_.append([{"LOWER": "невероятный"}, {"OP": "+"}, {"LOWER": "профит"}])
        self.spamPatterns_.append([{"LOWER": "огромный"}, {"OP": "+"}, {"LOWER": "выгода"}])
        self.spamPatterns_.append([{"LOWER": "невероятный"}, {"OP": "+"}, {"LOWER": "выгода"}])

        #russian - suggestions

        self.spamPatterns_.append([{"LOWER": "продать"}, {"OP": "+"}, {"LOWER": "криптовалюта"}])
        self.spamPatterns_.append([{"LOWER": "купить"}, {"OP": "+"}, {"LOWER": "криптовалюта"}])
        self.spamPatterns_.append([{"LOWER": "обменять"}, {"OP": "+"}, {"LOWER": "криптовалюта"}])
        self.spamPatterns_.append([{"LOWER": "обмен"}, {"OP": "+"}, {"LOWER": "криптовалюта"}])

        # english - motivation phrases
        self.spamPatterns_.append([{"LOWER": "join"}, {"OP": "+"}, {"LOWER": "now"}])
        self.spamPatterns_.append([{"LOWER": "subscribe"}, {"OP": "+"}, {"LOWER": "us"}])
        self.spamPatterns_.append([{"LOWER": "subscribe"}, {"OP": "+"}, {"LOWER": "channel"}])
        self.spamPatterns_.append([{"LOWER": "join"}, {"OP": "+"}, {"LOWER": "team"}])
        self.spamPatterns_.append([{"LOWER": "huge"}, {"OP": "+"}, {"LOWER": "profit"}])
        self.spamPatterns_.append([{"LOWER": "huge"}, {"OP": "+"}, {"LOWER": "profits"}])

        # english - scam
        self.spamPatterns_.append([{"LOWER": "eth"}, {"OP": "+"}, {"LOWER": "giveaway"}])
        self.spamPatterns_.append([{"LOWER": "btc"}, {"OP": "+"}, {"LOWER": "giveaway"}])
        self.spamPatterns_.append([{"LOWER": "pump"}, {"OP": "+"}, {"LOWER": "channel"}])
        self.spamPatterns_.append([{"LOWER": "rocket"}, {"OP": "+"}, {"LOWER": "pump"}])
        self.spamPatterns_.append([{"LOWER": "get"}, {"OP": "+"}, {"LOWER": "your"}, {"OP": "+"}, {"LOWER": "profit"}])
        self.spamPatterns_.append([{"LOWER": "rocket"}, {"OP": "+"}, {"LOWER": "pumps"}])


        self.spamPhraseMatcher_ = Matcher(self.nlp_.vocab)

        i = 0
        while i < len(self.spamPatterns_):
            self.spamPhraseMatcher_.add(str(i), None, self.spamPatterns_[i])
            i += 1

        return

    def analyze(self, doc):
        tokens = self.nlp_(doc)
        lemmatized_word_list = self.lemmatize_tokens(tokens)
        lemmatized_tokens = self.nlp_(" ".join(lemmatized_word_list))

        message_lines = list(map(lambda x: x.strip(), doc.split('\n')))
        emojis_count = 0
        for sym in message_lines:
            if len(sym) > 0:
                if sym[0] in UNICODE_EMOJI:
                    emojis_count += 1

        links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', doc)

        matches = self.spamPhraseMatcher_(tokens)
        if len(matches) > 1:
            return "spam"

        matches = self.spamPhraseMatcher_(lemmatized_tokens)
        if len(matches) > 1 or len(matches) > 0 and len(links) > 0:
            return "spam"
        elif emojis_count >= 5:
            return "spam"
        else:
            return "not spam"

    def lemmatize_tokens(self, tokens):
        res = []
        for t in tokens:
            cleaned_token = self.morph_.parse(t.text)[0].normal_form
            res.append(cleaned_token)
        return res

    se_ = None
    nlp_ = None
    morph_ = None
    spamPhraseMatcher_ = None

    spamPatterns_ = None
