###################################
#sudo apt-get install python-enchant
#pip install pyenchant
#sudo apt-get install hunspell-fr
#sudo apt-get install hunspell-ar

import conf
import json
import enchant
from fuzzywuzzy import fuzz
from nltk.stem import SnowballStemmer
#stemmer = SnowballStemmer(conf.LANGUAGE)

#import for filtred words
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import shutil as shu
import glob

#import for stop words tunisian arabic
import stop_words_tunisian_arabic

#import for get stem words tunisian arabic
from snowball_stemmer_tunisian import Arabic_Tunisian_Stemmer

# os.chdir(conf.PATH_PROJECT+'/data_corrector')
# os.chdir(conf.PATH_PROJECT)


#function filter sentence
def filter_sentens(language,text):
    text = text.lower()
    text = text.replace("'", " ")
    if (language == "tunisian"):
        stopWords = stop_words_tunisian_arabic.get_stopWordsTunisian()
    else:
        deff = conf.INGONRE_STOP_WORDS
        stopWords = set(stopwords.words(language))
        stopWords = stopWords - deff
    words = word_tokenize(text)
    wordsFiltered = ""

    for w in words:
        if w not in stopWords:
            wordsFiltered = wordsFiltered + " " + w

    return wordsFiltered.strip()

def extract_question(json_in, file,id_user,id_agent):

    with open(json_in,encoding='utf-8') as json_data:
        intents = json.load(json_data)

    sentens = []

    # loop through each sentence in our intents patterns
    for intent in intents['data']:
        for pattern in intent['patterns']:
            sent=str(pattern).replace("-", " ").lower()
            sent=sent.replace(","," ")
            #sent=str(sent).replace("â", "a")
            #sent = str(sent).replace("ç", "c")
            sentens.append(sent)
    with open(conf.PATH_PROJECT+"/data_corrector/folder_user_"+str(id_user)+"/agent_"+str(id_agent)+"/"+file, "a", encoding='utf-8')as out:
        for s in sentens:
            out.write(s + "\n")
    out.close()
    return 0

def generate_enchant_dict(file_name, out_file,id_user,language,id_agent):

    with open(conf.PATH_PROJECT+"/data_corrector/folder_user_"+str(id_user)+"/agent_"+str(id_agent)+"/"+file_name, 'r', encoding='utf-8')as f:
        text= f.read()
    f.close()
    text = filter_sentens(language,text)
    text= text.replace("\n", " ")
    text= text.replace("?", "")
    text=text.lower()
    words= word_tokenize(text)
    words = sorted(list(set(words)))
    with open(conf.PATH_PROJECT+"/data_corrector/folder_user_"+str(id_user)+"/agent_"+str(id_agent)+"/"+out_file, "w", encoding='utf-8')as out:
        for w in words:
            out.write(w + "\n")
    out.close()
    return words

def correct_words(spellchecker, text, language):
    text = text.lower()
    text = text.replace("?","")
    word_list = word_tokenize(text)

    if (language == "tunisian"):
        stemmer = Arabic_Tunisian_Stemmer()
    else:
        stemmer = SnowballStemmer(language)
    # auto-correct words
    corrected = []
    for w in word_list:
        ok = spellchecker.check(w)   # check spelling
        if not ok:
            suggestions = spellchecker.suggest(w)
            if len(suggestions) > 0:  # there are suggestions
                best = suggestions[0]#.decode(enc)   # best suggestions (decoded to str)
                if fuzz.ratio(stemmer.stem(w), stemmer.stem(best)) >= 75:
                    corrected.append(best)
                else:
                    corrected.append(w)
                #corrected.append(best)
            else:
                corrected.append(w)  # there's no suggestion for a correct word
        else:
            corrected.append(w)   # this word is correct
    sentens = ""
    for word in corrected:
        sentens = sentens + " " + word
    return sentens.strip()





