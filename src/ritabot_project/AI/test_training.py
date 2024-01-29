# -*- coding: utf-8 -*

import load_model_training
import conf
import os
# import for chatbot
import tensorflow as tf
import json
# import for filtred words
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



class test_trainer():

    chemin_data = conf.PATH_PROJECT + "/data/"
    chemin_absolut=""
    chemin_corrector = conf.PATH_PROJECT + "/data_corrector/"
    file=""
    id_user=0
    id_agent=0
    chat=None
    language=""
    def __init__(self,language,id_user,file,id_agent):

        self.chemin_absolut = conf.PATH_PROJECT + "/data_trainer_output/folder_user_"+str(id_user)+"/"
        self.file=file
        self.id_user=id_user
        self.id_agent=id_agent
        self.language=language


    """for element in os.listdir(chemin_data):
        if (element.endswith('.json')):
            correcter.extract_question(chemin_data + element, chemin_corrector + "veritas.txt")
            correcter.generate_enchant_dict(chemin_corrector + "veritas.txt", chemin_corrector + "veritas_dict.txt")
            cheker = correcter.enchant.request_pwl_dict(chemin_corrector + "veritas_dict.txt")"""

    # function filter sentence
    def filter_sentens(self,text):
        text = text.lower()
        text = text.replace("'", " ")
        text = text.replace("-", " ")
        text = text.replace(",", "")
        deff = conf.INGONRE_STOP_WORDS
        stopWords = set(stopwords.words(self.language))
        stopWords = stopWords - deff
        words = word_tokenize(text)
        wordsFiltered = ""

        for w in words:
            if w not in stopWords:
                wordsFiltered = wordsFiltered + " " + w

        if(len(wordsFiltered.strip()) <=1 ):
            wordsFiltered=""
        return wordsFiltered.strip()

    # path, dirs, files = next(os.walk(conf.PATH_PROJECT + "/data_trainer_output/"))
    def load_model_training(self):

        folders = conf.PATH_PROJECT + '/data_trainer_output/folder_user_'+str(self.id_user)+'/agent_'+str(self.id_agent)
        tf.reset_default_graph()
        self.chat = load_model_training.trainer(self.language)
        self.chat.load_pickel_file(folders + '/training_data')
        self.chat.load_json_file(folders + "/trainer_data.json")
        self.chat.set_tags()
        self.chat.Build_neural_network()
        self.chat.load_our_saved_model(folders + "/model.tflearn")

    def get_reply(self,question):
        data = []
        question = question.lower()
        if (question != ""):
            # question = question.replace("'", " ")
            value = question
            question = question.replace("-", " ")
            question = question.replace("?", "")
            question = question.replace("ç", "c")
            question = question.replace(",", "")
            question = question.replace("â", "a")

            # filter words
            question = self.filter_sentens(question)
            # corrector sentence
            #question = str(correcter.correct_words(self.cheker, question))
            # transtate sentence

            reply = "vide"

            if (self.chat.response(question, userID='123', show_details=False)):
                reply = self.chat.response(question, userID='123', show_details=False)

            if (reply):
                responses = str(reply[0])
                obj = reply[1]
                tag = reply[2]

            return reply

    def get_precision(self):

        # import our chat-bot intents file

        with open(conf.PATH_PROJECT + '/data/folder_user_' + str(self.id_user) + '/agent_' + str(self.id_agent) + '/' + self.file) as json_data:
            intents = json.load(json_data)

        tags = intents.keys()
        nb_pattern = 0
        nb_reply_false = 0
        for t in tags:
            for intent in intents[t]:
                for pattern in intent['patterns']:
                    """nb_pattern += 1
                    if (self.get_reply(pattern)[2] != intent['tag']):
                        nb_reply_false += 1
                        print("___________________________________________________________")
                        print("réponse de qustion | " + pattern + ":  false")"""
                    #print("patternss: ",self.filter_sentens(pattern))
                    print("midooo:", self.get_reply(pattern))
                    if(self.filter_sentens(pattern) != ""):
                        nb_pattern += 1

                        if (self.get_reply(pattern)[2] != intent['tag']):
                            nb_reply_false += 1
                            print("___________________________________________________________")
                            print("réponse de qustion | " + pattern + ":  false")

        print("___________________________________________________________")
        print("La pècision de votre chatbot est:====> " + str(nb_pattern - nb_reply_false) + "/" + str(
            nb_pattern) + ",  percentage: " + str(round(((nb_pattern - nb_reply_false) * 100) / nb_pattern, 2)) + "%")
        return (round(((nb_pattern - nb_reply_false) * 100) / nb_pattern, 2)),round(((nb_pattern - nb_reply_false) * 100) / nb_pattern, 2)

"""
t=test_trainer(123,"trainer_data_1.json")
t.load_model_training()
t.get_precision()"""