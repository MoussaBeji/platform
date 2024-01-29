# -*- coding: utf-8 -*

# import for chatbot
# things we need for NLP
import nltk
# from nltk.stem.lancaster import LancasterStemmer
# stemmer = LancasterStemmer()
from nltk.stem import SnowballStemmer

#stemmer = SnowballStemmer(conf.LANGUAGE)
# things we need for Tensorflow
import numpy as np
import tflearn
import random
# restore all of our data structures
import pickle
import json
import time
import conf
import phonenumbers

#import for get stem words tunisian arabic
from snowball_stemmer_tunisian import Arabic_Tunisian_Stemmer

#import for entity
import requests
from nltk.tokenize import  word_tokenize
import re


class trainer():

    words = []
    classes = []
    train_x = []
    train_y = []
    intents = {}
    tags = ()
    model = None
    context = {}
    session = {}
    entity = {}
    require ={}
    ERROR_THRESHOLD = conf.ERROR_THRESHOLD
    language=""

    def __init__(self,language):
        self.language=language


    def load_pickel_file(self,file):
        data = pickle.load(open(file, "rb"))
        self.words = data['words']
        self.classes = data['classes']
        self.train_x = data['train_x']
        self.train_y = data['train_y']



    def load_json_file(self,file):
        with open(file) as json_data:
            self.intents = json.load(json_data)



    def set_tags(self):
        self.tags=self.intents.keys()



    def Build_neural_network(self):
        net = tflearn.input_data(shape=[None, len(self.train_x[0])])
        net = tflearn.fully_connected(net, conf.NB_NEURONS)
        net = tflearn.fully_connected(net, conf.NB_NEURONS)
        net = tflearn.fully_connected(net, len(self.train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        self.model = tflearn.DNN(net)

    def clean_up_sentence(self, sentence):
        # tokenize the pattern
        sentence_words = nltk.word_tokenize(sentence)
        # stem each word
        if (self.language == "tunisian"):
            stemmer = Arabic_Tunisian_Stemmer()
        else:
            stemmer = SnowballStemmer(self.language)
        sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def bow(self,sentence, words, show_details=False):
        # tokenize the pattern
        sentence_words = self.clean_up_sentence(sentence)
        # bag of words
        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)

        return (np.array(bag))

    def load_our_saved_model(self,file):
        #tf.reset_default_graph()
        self.model.load(file)

    def classify(self,sentence):
        return_list = []
        if not (1 in self.bow(sentence, self.words)):
            return return_list

        # ERROR_THRESHOLD=max(self.model.predict([self.bow("azdjrhjhfgrj45erjer87grgrencfeyfdhgffgfj", self.words)])[0])
        # generate probabilities from the model
        results = self.model.predict([self.bow(sentence, self.words)])[0]
        #print("resultats=", results)
        # filter out predictions below a threshold
        #results = [[i, r] for i, r in enumerate(results) if r > self.ERROR_THRESHOLD]
        results = [[i, r] for i, r in enumerate(results) if r > (self.ERROR_THRESHOLD)]
        #print("resultats_2=", type(results))
        #print(" ERROR=", ERROR_THRESHOLD)
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)

        for r in results:
            return_list.append((self.classes[r[0]], r[1]))
        # return tuple of intent and probability
        #print("listprob: ",return_list)
        return return_list



    #Fulfillment
    def fulfillment(self, question, user_id, user_infos, entitys, mycode):
        l = locals()
        l['response'] = ""
        l['object'] = {"type": "simple", "value": {}}
        mycode = str(entitys) + ";" + mycode
        code = compile(mycode, '<string>', 'exec')
        exec(code)
        return l['response'], l['object']

    #new add for entity
    def get_prompt(self, userID, user_infos, question):

        prompts = None
        probability = 0
        data = self.entity[userID]["entity_value"]
        language = self.entity[userID]["language"]
        data['LANGUAGE'] = language
        data['SENTENCE'] = question
        tag = self.entity[userID]["tag"]
        response = self.entity[userID]["response"]
        objects = self.entity[userID]["object"]
        entity = self.entity[userID]["entity"]
        fulfillment_exist = self.entity[userID]["fulfillment_exist"]
        mycode = self.entity[userID]["mycode"]
        req = {}
        # api-endpoint
        URL = conf.URL+":5000/entity"
        if 'check_entity' in self.entity[userID]:
            req=[{"start": 0, "end": len(question), "text": question, "type": self.entity[userID]["check_entity"], "value": question}]
            response = response.replace('$'+self.entity[userID]["check_entity"], question)
            entity[self.entity[userID]["check_entity"]] = question
        else:
            r = requests.get(url=URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
            req = r.json()["data"]
        exist_entity = False
        check_entity = ""
        if req:
            exist_entity = True

        for i in self.intents["data"]:
            if(i["tag"] == tag):
                words = response.split(" ")
                words.reverse()
                print("klklmklmklmk:", words)
                for word in words:
                    if (word[0] == '$'):
                        word_1 = re.sub(r'[$|.|,|;|:|?|!]', '', word)
                        exist = False
                        check_entity = ""
                        for e in req:
                            if word_1 == e['type']:
                                response = response.replace(word, e['value'])
                                entity[word_1] = e['value']
                                exist = True
                        if not exist:
                            if (isinstance(i['entity'][word_1]["value"], bool)):
                                prompts = i['entity'][word_1]["prompt"]
                                objects = {"type": "simple", "value": {}}
                            elif (i['entity'][word_1]["value"][0] == "*****"):
                                prompts = i['entity'][word_1]["prompt"]
                                objects = {"type": "simple", "value": {}}
                                # check_entity = word_1
                            else:
                                prompts = "custom"
                                objects = {
                                    "type": "nested",
                                    "value": {
                                        "text1": "",
                                        "obj1": {
                                            "text": i['entity'][word_1]["prompt"],
                                            "quick_replies": [
                                                {"content_type": "text", "title": boutton, "payload": boutton} for
                                                boutton in i['entity'][word_1]['value']]
                                        }
                                    }
                                }

                words = response.split(" ")
                words.reverse()
                for word in words:
                    if (word[0] == '$'):
                        check_entity = ""
                        word_1 = re.sub(r'[$|.|,|;|:|?|!]', '', word)
                        if (isinstance(i['entity'][word_1]["value"], bool)):
                            pass
                        elif(i['entity'][word_1]["value"][0] == "*****"):
                            check_entity = word_1

        self.entity[userID]["response"] = response
        if prompts:
            if prompts == "custom":
                msg = ""
            else:
                msg = prompts
            self.entity[userID] = {"tag": tag, "probability": self.entity[userID]["probability"], "language": language, "response": response,"entity_value": self.entity[userID]["entity_value"], "object": self.entity[userID]["object"], "entity": entity, "fulfillment_exist": fulfillment_exist, "mycode": mycode }
            self.session[userID] = time.time() // 60
            if check_entity != "":
                self.entity[userID]["check_entity"] = check_entity
            print(self.entity[userID])
        else:
            msg =response
            objects = self.entity[userID]["object"]
            print("entitysss:", self.entity[userID]["entity"])
            del self.entity[userID]
            if  fulfillment_exist:
                try:
                    msg, objects = self.fulfillment(question, userID, user_infos, entity, mycode)
                except:
                    msg = "erreur de compilation"

        return msg, objects, tag, probability, exist_entity


    def response(self,language,value,sentence, userID, gender, user_infos, show_details=False):

        # new code for entity
        prompts = None
        if(userID in self.entity):
            msg, objects, tag, prob, exist_entity = self.get_prompt(userID, user_infos, value)
            if exist_entity or not self.classify(sentence):
                return msg, objects, tag, prob
            del self.entity[userID]
        results = self.classify(sentence)
        #hhhhhhhhh
        if not results:
            if userID in self.require:
                if self.require[userID]["nb_tentative"] != 0:
                    for j in self.intents["data"]:
                        if (j["tag"] == self.require[userID]["redirection"]):
                            tag = j['tag']
                            probability = 0
                            if gender not in j['block_response']:
                                gender = "default"
                            msg = random.choice(j["block_response"][gender]['responses']).strip()
                            objects = random.choice(j["block_response"][gender]['object'])
                    self.require[userID]["nb_tentative"] = self.require[userID]["nb_tentative"] - 1
                else:
                    for j in self.intents["data"]:
                        if (j["tag"] == self.require[userID]["echec"]):
                            tag = j['tag']
                            probability = 0
                            if gender not in j['block_response']:
                                gender = "default"
                            msg = random.choice(j["block_response"][gender]['responses']).strip()
                            objects = random.choice(j["block_response"][gender]['object'])
                    del self.require[userID]
                return msg, objects, tag, probability

        # sorted list probality
        r = []
        cont = False
        while results:
            for t in self.tags:
                for i in self.intents[t]:
                    # find a tag matching the first result

                    if i['tag'] == results[0][0]:
                        if ('context_filter' in i):
                            r.insert(0, results[0])
                            cont = True
                        else:
                            r.insert(len(results), results[0])
            results.pop(0)
        try:
            if not cont:
                del self.context[userID]
        except:
            print("error!!!")
        results = r

        # if we have a classification then find the matching intent tag
        if results:
            # loop as long as there are matches to process
            while results:
                for t in self.tags:
                    for i in self.intents[t]:
                        # find a tag matching the first result
                        if i['tag'] == results[0][0]:
                            probability = results[0][1]
                            # check if this intent is contextual and applies to this user's conversation
                            #if not 'context_filter' in i or (userID in self.context and 'context_filter' in i and i['context_filter'][0] == self.context[userID]):
                            if not 'context_filter' in i or (userID in self.context and 'context_filter' in i and set(i['context_filter']).intersection(set(self.context[userID]))):
                                if show_details: print('tag:', i['tag'])
                                # a random response from the intent
                                if gender not in i['block_response']:
                                    gender ="default"
                                msg = random.choice(i["block_response"][gender]['responses']).strip()
                                objects = random.choice(i["block_response"][gender]['object'])
                                tag = i['tag']

                                # set context for this intent if necessary
                                if 'context_set' in i:
                                    if show_details: print('context:', i['context_set'])
                                    self.context[userID] = i['context_set']
                                    self.session[userID] = time.time() // 60
                                print("context:", self.context)
                                print("sessions:", self.session)
                                #new code for require intents
                                if userID in self.require:
                                    #if tag in self.require[userID]["depondant"] or self.require[userID]["nb_tentative"] == 0:
                                    if tag in self.require[userID]["depondant"]:
                                        del self.require[userID]
                                    elif  self.require[userID]["nb_tentative"] != 0:
                                        for j in self.intents["data"]:
                                            if (j["tag"] == self.require[userID]["redirection"]):
                                                tag = j['tag']
                                                probability = 0
                                                if gender not in j['block_response']:
                                                    gender = "default"
                                                msg = random.choice(j["block_response"][gender]['responses']).strip()
                                                objects = random.choice(j["block_response"][gender]['object'])
                                        self.require[userID]["nb_tentative"] = self.require[userID]["nb_tentative"] - 1
                                    else:
                                        for j in self.intents["data"]:
                                            if (j["tag"] == self.require[userID]["echec"]):
                                                tag = j['tag']
                                                probability = 0
                                                if gender not in j['block_response']:
                                                    gender = "default"
                                                msg = random.choice(j["block_response"][gender]['responses']).strip()
                                                objects = random.choice(j["block_response"][gender]['object'])
                                        del self.require[userID]
                                if 'require' in i :
                                    self.require[userID] = i["require"].copy()
                                    self.session[userID] = time.time() // 60

                                #new code for entity
                                fulfillment_exist = False
                                mycode = ""
                                check_entity = ""
                                if 'Fulfillment' in i:
                                    fulfillment_exist =True
                                    mycode = str(i['Fulfillment']['code'])
                                if 'entity' in i:
                                    entity = {}
                                    data = i['entity'].copy()
                                    data['LANGUAGE'] = language
                                    data['SENTENCE'] = value

                                    # api-endpoint
                                    URL = conf.URL+":5000/entity"
                                    r = requests.get(url=URL, data=json.dumps(data),headers={"Content-Type": "application/json"})
                                    req = r.json()["data"]
                                    if fulfillment_exist:
                                        words = i['Fulfillment']['entitys'].copy()
                                        msg = ' '.join(i['Fulfillment']['entitys'])
                                        words.reverse()
                                    else:
                                        words = msg.split(" ")
                                        words.reverse()
                                    # words = msg.split(" ")
                                    print('mmmmmmm:',words)
                                    for word in words:
                                        if(word[0] == '$'):
                                            word_1 = re.sub(r'[$|.|,|;|:|?|!]', '', word)
                                            exist = False
                                            check_entity =""
                                            for e in req:
                                                if word_1 == e['type']:
                                                    msg = msg.replace(word,e['value'])
                                                    entity[word_1] = e['value']
                                                    exist = True
                                            if not exist:
                                                if(isinstance(i['entity'][word_1]["value"], bool)):
                                                    prompts = i['entity'][word_1]["prompt"]
                                                    objects = {"type": "simple","value": {}}

                                                elif(i['entity'][word_1]["value"][0] == "*****"):
                                                    prompts = i['entity'][word_1]["prompt"]
                                                    objects = {"type": "simple", "value": {}}
                                                    check_entity = word_1

                                                else:
                                                    prompts = "custom"
                                                    objects = {
                                                        "type": "nested",
                                                        "value": {
                                                            "text1": "",
                                                            "obj1": {
                                                                "text": i['entity'][word_1]["prompt"],
                                                                "quick_replies": [
                                                                    {"content_type": "text", "title": boutton,
                                                                     "payload": boutton} for boutton in
                                                                    i['entity'][word_1]['value']]
                                                            }
                                                        }
                                                    }

                                    entitys_response = msg
                                    if prompts:
                                        if prompts == "custom":
                                            msg = ""
                                        else:
                                            msg = prompts
                                        self.entity[userID] = {"tag": tag, "probability": probability,"language": language ,"response": entitys_response, "entity_value": i['entity'], "object": objects, "entity": entity, "fulfillment_exist": fulfillment_exist, "mycode": mycode }
                                        self.session[userID] = time.time() // 60
                                        if check_entity != "":
                                            self.entity[userID]["check_entity"] = check_entity
                                    if not prompts and fulfillment_exist:
                                        try:
                                            msg, objects = self.fulfillment(value, userID, user_infos, entity, mycode)
                                        except:
                                            msg ="erreur de compilation"

                                print("entitysss:", self.entity)
                                print("require:",self.require)
                                return msg, objects, tag, probability

                results.pop(0)



