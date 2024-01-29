
import conf
from nltk.corpus import stopwords

def get_stopWordsTunisian():
    stopWordsTunisian = None
    with open(conf.PATH_PROJECT + "/stop-words-tunisian-arabic/tunisian.txt") as file:
        # stopWordsTunisian.append(file.read())
        stopWordsTun = file.readlines()

    stopWordsTunisian =[]
    for l in stopWordsTun:
        stopWordsTunisian.append(l.rstrip('\n'))

    stopWords = set(stopwords.words("arabic") + stopWordsTunisian)
    return stopWords

get_stopWordsTunisian()