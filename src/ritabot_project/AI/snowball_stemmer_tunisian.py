
import re
from nltk.stem.util import suffix_replace, prefix_replace
# suffixes = ["ي", "نا", "ك", "كم", "ه", "هم", "ها", "لي", "لنا", "لك", "لكم", "له", "لهم", "لها", "وا",
#                 "و", "ني", "ت" ]
# prefixes = ["ن", "ت", "ي", "ال"]

class Arabic_Tunisian_Stemmer():

    is_verb = True
    is_noun = True
    is_defined = False
    # Normalize_pre stes
    __vocalization = re.compile(r"[\u064b-\u064c-\u064d-\u064e-\u064f-\u0650-\u0651-\u0652]")  # ً، ٌ، ٍ، َ، ُ، ِ، ّ، ْ

    __kasheeda = re.compile(r"[\u0640]")  # ـ tatweel/kasheeda

    __arabic_punctuation_marks = re.compile(r"[\u060C-\u061B-\u061F]")  # ؛ ، ؟

    __articles_3len = ("\u0648\u0627\u0644", "\u0641\u0627\u0644", "\u0643\u0627\u0644", "\u0628\u0627\u0644", "bil", "bel", "kel", "kil", "fel", "fil", "wel", "wil", "mel", "mil", "mill", "mell")  # بال كال فال وال

    __articles_2len = ("\u0627\u0644", "\u0644\u0644","el", "al", "lel")  # ال لل

    __suffix_noun_step2c2 = "\u0629"  # ة

    __prefix_step3a_noun = (
        "\u0648\u0627\u0644",  # وال
        "\u0641\u0627\u0644",  # فال
        "\u0627\u0644",
        "\u0644\u0644",  # لل، ال
        "\u0643\u0627\u0644",
        "\u0628\u0627\u0644",  # بال، كال
        "wel",  # wel
        "fel",  # fel
        "el",
        "lel",  # el lel
        "kel",
        "bel"  # kel bel
    )

    # Checks
    __checks1 = (
        "\u0648\u0627\u0644", # وال
        "\u0641\u0627\u0644", # فال
        "\u0643\u0627\u0644",
        "\u0628\u0627\u0644",  # بال، كال
        "\u0627\u0644",
        "\u0644\u0644",  # لل، ال
        "wel",  # wel
        "fel",  # fel
        "el",
        "lel",  # el lel
        "kel",
        "bel",  # kel bel
    )

    __checks2 = ("\u0629", "\u0627\u062a")  # ة  #  female plural ات

    __suffixes_verb = (
        "\u0644\u0643",  # لك
        "\u0644\u0646\u0627",  # لنا
        "\u0644\u0647\u0627",  # لها
        "\u0644\u0647\u0645",  # لهم
        "\u0644\u0643\u0645",  # لكم
        "\u0644\u0647",  # له
        "\u0644\u064a",  # لي
        "\u0646\u064a",  # ني
        "\u0643\u0645",  # كم
        "\u0647\u0645",  # هم
        "\u0647\u0627",  # ها
        "\u0648\u0627",  # وا
        "\u064a",  # ي
        "\u0646\u0627",  # نا
        "\u0643",  # ك
        "\u0647",  # ه
        "\u0648",  # و
        "\u062a",  # ت
        "lak",  # lak
        "lik",  # lik
        "lek",  # lek
        "elna",  # elna
        "elha",  # elha
        "elhom",  # elhom
        "elkom",  # elkom
        "lah",  # lah
        "li",  # li
        "ni",  # ni
        "kom",  # kom
        "hom",  # hom
        "ha",  # ha
        "he",  # he
        "ou",  # ou
        "ew",   # ew
        "i",  # i
        "na",  # na
        "ne",   # ne
        "ouch",  # fhemt + ouch
        "ich"  # fhemt + ich
    )

    #normalize post
    __last_hamzat = ("\u0623", "\u0625", "\u0622", "\u0624", "\u0626")  # أ، إ، آ، ؤ، ئ

    __initial_hamzat = re.compile(r"^[\u0622\u0623\u0625]")  # أ، إ، آ

    __waw_hamza = re.compile(r"[\u0624]")  # ؤ

    __yeh_hamza = re.compile(r"[\u0626]")  # ئ

    __alefat = re.compile(r"[\u0623\u0622\u0625]")  #

    #normalized word type string
    def __normalize_pre(self, token):

        # strip diacritics
        word = self.__vocalization.sub("", token)
        # strip kasheeda
        word = self.__kasheeda.sub("", word)
        # strip punctuation marks
        word = self.__arabic_punctuation_marks.sub("", word)
        return word


    def __checks_1(self, token):
        for prefix in self.__checks1:
            if token.startswith(prefix):
                if prefix in self.__articles_3len and len(token) > 4:
                    self.is_noun = True
                    self.is_verb = False
                    self.is_defined = True
                    break

                if prefix in self.__articles_2len and len(token) > 3:
                    self.is_noun = True
                    self.is_verb = False
                    self.is_defined = True
                    break


    def __checks_2(self, token):
        for suffix in self.__checks2:
            if token.endswith(suffix):
                if suffix == "\u0629" and len(token) > 2:
                    self.is_noun = True
                    self.is_verb = False
                    break

                if suffix == "\u0627\u062a" and len(token) > 3:
                    self.is_noun = True
                    self.is_verb = False
                    break


    def __Prefix_Step3a_Noun(self, token):
        for prefix in self.__prefix_step3a_noun:
            if token.startswith(prefix):
                if prefix in self.__articles_2len and len(token) > 4:
                    token = token[len(prefix):]
                    self.prefix_step3a_noun_success = True
                    break
                if prefix in self.__articles_3len and len(token) > 5:
                    token = token[len(prefix):]
                    break
        return token

    def __Suffix_Noun_Step2c2(self, token):
        for suffix in self.__suffix_noun_step2c2:
            if token.endswith(suffix) and len(token) >= 3:
                token = token[:-1]
                self.suffix_noun_step2c2_success = True
                break
        return token


    def __Suffix_verb(self, token):
        for suffix in self.__suffixes_verb:
            if token.endswith(suffix):
               token = suffix_replace(token, suffix, "")
               break
        return token

    def __normalize_post(self, token):
        # normalize last hamza
        # for hamza in self.__last_hamzat:
        #     if token.endswith(hamza):
        #         token = suffix_replace(token, hamza, "\u0621")
        #         break
        # normalize other hamzat
        token = self.__initial_hamzat.sub("\u0627", token)
        # token = self.__waw_hamza.sub("\u0648", token)
        token = self.__yeh_hamza.sub("\u064a", token)
        # token = self.__alefat.sub("\u0627", token)
        return token


    #Stem an Tunisian Arabic word and return the stemmed form
    def stem(self, word):

        # set initial values
        self.is_verb = True
        self.is_noun = True
        self.is_defined = False

        modified_word = word
        # guess type and properties
        # checks1
        self.__checks_1(modified_word)
        # checks2
        self.__checks_2(modified_word)
        # Pre_Normalization
        modified_word = self.__normalize_pre(modified_word)

        # print("Is verb:",self.is_verb)
        # print("Is noun:",self.is_noun)

        if(self.is_noun):
            modified_word = self.__Prefix_Step3a_Noun(modified_word)
            modified_word = self.__Suffix_Noun_Step2c2(modified_word)
            # print("modified word:", modified_word)

        if(self.is_verb):
            modified_word = self.__Suffix_verb(modified_word)
            # print("modified word:", modified_word)

        # post normalization stemming
        modified_word = self.__normalize_post(modified_word)
        # print("modified word:", modified_word)
        return modified_word


# Arabic_Tunisian_Stemmer().stem("3endkom")

