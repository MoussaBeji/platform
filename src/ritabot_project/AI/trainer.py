# -*- coding: utf-8 -*-

import conf
# things we need for NLP
import nltk
nltk.download('stopwords')
nltk.download('punkt')
# from nltk.stem.lancaster import LancasterStemmer
# stemmer = LancasterStemmer()
from nltk.stem import SnowballStemmer
#stemmer = SnowballStemmer(conf.LANGUAGE)
# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random
import json
# import for filtred words
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from shutil import copyfile
import pickle
import shutil
import subprocess
import requests

#import for test corpus
#import test_training

#import for stop words tunisian arabic
import stop_words_tunisian_arabic

#import for get stem words tunisian arabic
from snowball_stemmer_tunisian import Arabic_Tunisian_Stemmer


class EarlyStoppingCallback(tflearn.callbacks.Callback):
    compter = 0
    max = 0

    def __init__(self, val_acc_thresh):
        """ Note: We are free to define our init function however we please. """
        # Store a validation accuracy threshold, which we can compare against
        # the current validation accuracy at, say, each epoch, each batch step, etc.
        self.val_acc_thresh = val_acc_thresh

    def on_epoch_end(self, training_state):
        """
        This is the final method called in trainer.py in the epoch loop.
        We can stop training and leave without losing any information with a simple exception.
        """
        print("Terminating training at the end of epoch", training_state.epoch)
        # raise StopIteration
        if(training_state.acc_value > 0.99):
            raise StopIteration
        if (training_state.epoch == conf.NB_EPOCH):
            raise StopIteration
        if(training_state.epoch <= conf.NB_EPOCH_THRESHOLD and self.max < 0.99):
            if training_state.acc_value >= self.max:
                self.max = training_state.acc_value
        else:
            if training_state.acc_value >= (self.max - 0.01):
                self.compter = self.compter + 1
            else:
                self.compter = 0
            if (self.compter > 1):
                raise StopIteration

    def on_train_end(self, training_state):
        """
        Furthermore, tflearn will then immediately call this method after we terminate training,
        (or when training ends regardless). This would be a good time to store any additional
        information that tflearn doesn't store already.
        """
        print("info:", training_state.acc_value)
        print("max:",self.max)

class training():
    train_x = []
    train_y = []

    # function filter sentence
    def filter_sentens(self, language, text):
        text = text.lower()
        text = text.replace("'", " ")
        text = text.replace("-", " ")
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

    def create_service(self, language, id_user, id_agent):
        port = 8000 + int(id_agent)
        file = "agent_" + str(port) + ".service"
        name = language + " " + str(id_user) + " " + str(id_agent)
        text = """[Unit]\nDescription=lanch agent has port {0}\nAfter=network.target\n\n[Service]\nUser={1}\nGroup=www-data\nWorkingDirectory={2}/data_trainer_output/folder_user_{4}/agent_{5}\nExecStart={3}/uwsgi --ini agent_{0}.ini\nRestart=always\n\n[Install]\nWantedBy=multi-user.target
        """.format(port, conf.NAME_USER, conf.PATH_PROJECT, conf.PROJECT_ENV, id_user, id_agent )
        agent_service = open(
            '{}/data_trainer_output/folder_user_{}/agent_{}/{}'.format(conf.PATH_PROJECT, id_user, id_agent, file),
            "w+")
        agent_service.write(text)
        agent_service.close()
        # cmd = "echo Solixy2020 | sudo -S cp -r "+conf.PATH_PROJECT + '/data_trainer_output/folder_user_' + str(id_user) + '/agent_' + str(id_agent) + '/' + file +" /etc/systemd/system"
        cmd_1 = "sudo chmod 777 -R " + conf.PATH_PROJECT + '/data_trainer_output/folder_user_' + str(id_user) + '/agent_' + str(id_agent) + "; "
        cmd_2 = "sudo cp -r " + conf.PATH_PROJECT + '/data_trainer_output/folder_user_' + str(id_user) + '/agent_' + str(id_agent) + '/' + file + " /etc/systemd/system"

        subprocess.Popen([cmd_1 + cmd_2], shell=True)


    def create_ini_file(self, id_user, id_agent, language):
        port = 7000 + int(id_agent)
        file = "agent_" + str(port+1000) + ".ini"
        text = """[uwsgi]\nchdir = {0}\nmodule = wsgi:application\npyargv = {5} {2} {3} {4}\nhttp = 0.0.0.0:{1}\nsocket = {0}/data_trainer_output/folder_user_{2}/agent_{3}/agent_{4}.sock\nchmod-socket = 660\nvacuum = true\nenable-threads = true\nthreads = 5\ndie-on-term = true
        """.format(conf.PATH_PROJECT, port, id_user, id_agent, port+1000, language)
        agent_ini_file = open(
            '{}/data_trainer_output/folder_user_{}/agent_{}/{}'.format(conf.PATH_PROJECT, id_user, id_agent, file),
            "w+")
        agent_ini_file.write(text)
        agent_ini_file.close()


    def create_proxy_request(self, id_user, id_agent):
        port = 8000 + int(id_agent)
        file = "agent_" + str(port)
        text = """server {{\nlisten {0} ssl;\nserver_name  {1};\n#config for ssl\n#listen 443;\nssl on;\nssl_certificate {2};\nssl_certificate_key {3};\nlocation / {{\ninclude uwsgi_params;\nuwsgi_pass unix:{4}/data_trainer_output/folder_user_{5}/agent_{6}/agent_{0}.sock;\n}}\n}}
        """.format(port, conf.SERVER_NAME, conf.SSL_CERTIFICATE, conf.SSL_CERTIFICATE_KEY, conf.PATH_PROJECT, id_user, id_agent)
        agent_proxy_file = open(
            '{}/data_trainer_output/folder_user_{}/agent_{}/{}'.format(conf.PATH_PROJECT, id_user, id_agent, file),
            "w+")
        agent_proxy_file.write(text)
        agent_proxy_file.close()
        cmd_1 = "sudo chmod 777 -R " + conf.PATH_PROJECT + '/data_trainer_output/folder_user_' + str(id_user) + '/agent_' + str(id_agent) + "; "
        cmd_2 = "sudo cp -r " + conf.PATH_PROJECT + '/data_trainer_output/folder_user_' + str(id_user) + '/agent_' + str(id_agent) + '/' + file + " /etc/nginx/sites-available" + "; "
        cmd_3 = "sudo ln -s /etc/nginx/sites-available/" + file + "  /etc/nginx/sites-enabled;"
        cmd_4 = "sudo service nginx restart"
        subprocess.Popen([cmd_1 + cmd_2 + cmd_3 + cmd_4], shell=True)


    def prepare_data_trainer(self, language, file, id_user,id_agent):
        # import our chat-bot intents file

        with open(conf.PATH_PROJECT + '/data/folder_user_' + str(id_user)+ '/agent_'+  str(id_agent) +'/' + file) as json_data:
            intents = json.load(json_data)
        words = []
        classes = []
        documents = []
        ignore_words = ['?']
        # loop through each sentence in our intents patterns
        # tags=["contact","Présentation","emploi et stage","Méthodologie"]
        # tags=["data"]
        tags = intents.keys()

        for t in tags:
            for intent in intents[t]:
                for pattern in intent['patterns']:
                    # tokenize each word in the sentence
                    pattern = str(pattern).replace("-", " ")
                    pattern = str(pattern).replace("ç", "c")
                    pattern = str(pattern).replace(",", "")
                    pattern = str(pattern).replace("â", "a")
                    print(pattern)
                    # filter words of stop_words
                    pattern = self.filter_sentens(language,pattern)
                    #print(pattern)
                    w = nltk.word_tokenize(pattern)
                    # add to our words list
                    words.extend(w)
                    #print("words: ", words)
                    # add to documents in our corpus
                    if(w):
                        documents.append((w, intent['tag']))
                    # add to our classes list
                    if intent['tag'] not in classes:
                        classes.append(intent['tag'])

        # stem and lower each word and remove duplicates
        if (language == "tunisian"):
            stemmer = Arabic_Tunisian_Stemmer()
        else:
            stemmer = SnowballStemmer(language)
        words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
        words = sorted(list(set(words)))
        print("stemmer: ", words)

        # remove duplicates
        classes = sorted(list(set(classes)))

        # print(len(documents), "documents")
        # print(len(classes), "classes", classes)
        # print(len(words), "unique stemmed words", words)

        # create our training data
        training = []
        output = []
        # create an empty array for our output
        output_empty = [0] * len(classes)

        # training set, bag of words for each sentence
        for doc in documents:
            # initialize our bag of words
            bag = []
            # list of tokenized words for the pattern
            pattern_words = doc[0]
            # stem each word
            pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
            # create our bag of words array
            for w in words:
                bag.append(1) if w in pattern_words else bag.append(0)

            # output is a '0' for each tag and '1' for current tag
            output_row = list(output_empty)
            output_row[classes.index(doc[1])] = 1

            training.append([bag, output_row])

        # shuffle our features and turn into np.array
        random.shuffle(training)
        training = np.array(training)
        # create train and test lists
        train_x = list(training[:, 0])
        train_y = list(training[:, 1])
        # reset underlying graph data
        tf.reset_default_graph()
        # Build neural network
        net = tflearn.input_data(shape=[None, len(train_x[0])])
        net = tflearn.fully_connected(net, conf.NB_NEURONS)
        net = tflearn.fully_connected(net, conf.NB_NEURONS)
        net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        folder_user = "folder_user_" + str(id_user)
        folder_agent = "agent_"+str(id_agent)
        # Define model and setup tensorboard
        model = tflearn.DNN(net,tensorboard_dir=conf.PATH_PROJECT + '/data_trainer_output/' + folder_user + '/'+ folder_agent + '/tflearn_logs',tensorboard_verbose=3)
        # Start training (apply gradient descent algorithm)
        # model.load('model.tflearn')



        early_stopping_cb = EarlyStoppingCallback(val_acc_thresh=0.1)
        try:
            model.fit(train_x, train_y, n_epoch=conf.NB_EPOCH, batch_size=conf.BATCH_SIZE, show_metric=True,callbacks=early_stopping_cb)
        except StopIteration:
            model.save(
                conf.PATH_PROJECT + '/data_trainer_output/' + folder_user + '/' + folder_agent + '/model.tflearn')
            pickle.dump({'words': words, 'classes': classes, 'train_x': train_x, 'train_y': train_y}, open(
                conf.PATH_PROJECT + "/data_trainer_output/" + folder_user + "/" + folder_agent + "/training_data",
                "wb"))
            copyfile(conf.PATH_PROJECT + '/data/folder_user_' + str(id_user) + '/agent_' + str(id_agent) + '/' + file,
                     conf.PATH_PROJECT + '/data_trainer_output/' + folder_user + '/' + folder_agent + '/trainer_data.json')
            shutil.rmtree(
                conf.PATH_PROJECT + '/data_trainer_output/' + folder_user + '/' + folder_agent + '/tflearn_logs')

        self.create_ini_file(id_user, id_agent, language)
        self.create_proxy_request(id_user, id_agent)
        self.create_service(language, id_user, id_agent)


        auth_token = 'ff5f834b3cd8b2ba52f862998138d5b9b2c63dd7'
        hed = {'Authorization': 'Token ff5f834b3cd8b2ba52f862998138d5b9b2c63dd7', 'Content-type': 'application/json'}
        # data = {'status': 'entrainer'}
        data = json.dumps({"status": "entrainer"})

        url = conf.URL+':8000/api/bot/agent_status/{}/'.format(id_agent)
        response = requests.post(url, data, headers=hed)  # verify=False



#training().prepare_data_trainer('tunisian','data.json',4,1)

