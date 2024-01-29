# -*- coding: utf-8 -*
#how to run flask server with gunicorn
#gunicorn --name="language id_user id_agent" --bind 0.0.0.0:5000 wsgi --certfile=domain.crt --keyfile=domain.key

import load_model_training
import conf
from flask_cors import CORS
from flask import Flask, jsonify
from flask import request
import tensorflow as tf
import random
import datetime
import json
# import for filtred words
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
import corrector as correcter
import glob
import os
import time
import requests
#Country Lookup library
import pygeoip
#lanche a crontab sheduling
import scheduling

#import for stop words tunisian arabic
import stop_words_tunisian_arabic

#import to flask limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


#get all arguments: language, id user, id agent, port
language = sys.argv[1]
id_user = sys.argv[2]
id_ag = sys.argv[3]
port = sys.argv[4]

#get all arguments: language, id user, id agent (for gunicorn)
# args = (str(sys.argv[1]).replace("--name=","")).split(" ")
# language = args[0]
# id_user = args[1]
# id_ag = args[2]
# port = str(sys.argv[3].replace('0.0.0.0:', ''))

#code crontab for launch crontab
name_service = "clear_context_" + str(id_user) + '_' + str(id_ag)
command =  conf.PROJECT_ENV + "/" + conf.CMD_PYTHON + ' ' + conf.PATH_PROJECT + '/clear_context.py ' + str(port)
schedul_context = scheduling.Scheduling(port, name_service, command)
schedul_context.launch()

#code crontab for the control status of agent
name_service = "agent_" + str(port)
command = conf.PROJECT_ENV + "/" + conf.CMD_PYTHON + ' ' + conf.PATH_PROJECT + '/check_status.py ' + str(port) + ' '+ name_service
schedul_service = scheduling.Scheduling(port, name_service, command)
schedul_service.launch()

#loads geoip database into memory
geo = pygeoip.GeoIP(conf.PATH_PROJECT+'/GeoIP/GeoIP.dat')

# corrector sentence
chemin_data=conf.PATH_PROJECT+"/data/folder_user_" + str(id_user) +"/agent_"+str(id_ag)+"/"
chemin_absolut=conf.PATH_PROJECT+"/data_trainer_output/"+'folder_user_'+str(id_user)+"/agent_"+str(id_ag)+"/"
chemin_corrector=conf.PATH_PROJECT+"/data_corrector/folder_user_" + str(id_user) + "∕"

try:
    os.stat(conf.PATH_PROJECT+"/data_corrector/folder_user_" + str(id_user) + "/agent_"+str(id_ag))
except:
    os.makedirs(conf.PATH_PROJECT+"/data_corrector/folder_user_" + str(id_user) + "/agent_"+str(id_ag))

r = glob.glob(conf.PATH_PROJECT + '/data_corrector/folder_user_'+str(id_user) + "/agent_"+str(id_ag) +'/*')
for f in r:
    os.remove(f)

for element in os.listdir(chemin_data):
    if(element.endswith('.json')):
        correcter.extract_question(chemin_data + element , "veritas.txt" , id_user , id_ag)
        correcter.generate_enchant_dict("veritas.txt" , "veritas_dict.txt" , id_user,language,id_ag)

cheker = correcter.enchant.request_pwl_dict(conf.PATH_PROJECT+"/data_corrector/folder_user_"+id_user+"/agent_"+id_ag+"/veritas_dict.txt")


"""from OpenSSL import SSL

context = SSL.Context(SSL.SSLv23_METHOD)
cer = os.path.join(os.path.dirname(__file__), './domain.crt')
key = os.path.join(os.path.dirname(__file__), './domain.key')"""

application = Flask(__name__)
application.config['JSON_AS_ASCII'] = False
cors = CORS(application, resources={r"/api/*": {"origins": "*"}})

limiter = Limiter(
    application,
    key_func=get_remote_address,
    # default_limits=["2 per minute", "1 per second"],
)

@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# function filter sentence
def filter_sentens(text):
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


path, dirs, files = next(os.walk(conf.PATH_PROJECT+"/data_trainer_output/"))
directory_count = len(dirs)



folder = conf.PATH_PROJECT+'/data_trainer_output/'+'folder_user_'+str(id_user)+"/agent_"+str(id_ag)

tf.reset_default_graph()
model = load_model_training.trainer(language)
model.load_pickel_file(folder+ "/" + "training_data")
model.load_json_file(folder + "/" + 'trainer_data.json')
model.set_tags()
model.Build_neural_network()
model.load_our_saved_model(folder + "/" + 'model.tflearn')



#load json file of response default
with open(conf.PATH_PROJECT + '/data/folder_user_' + str(id_user) + '/agent_' + str(id_ag) + '/non_response.json') as json_data:
    intents_dfault_response = json.load(json_data)

def get_intents_default(token, gender):
    for intent in intents_dfault_response["data"]:
        if intent["patterns"][0] == token:
            if token == "a45ec879abd5879fd545ae545ccv6910ab3ffe59":
                return intent["tag"], intent['responses'], intent['object']
            if gender not in intent['block_response']:
                gender = "default"
            response = random.choice(intent["block_response"][gender]['responses']).strip()
            objects = random.choice(intent["block_response"][gender]['object'])
            return intent["tag"], response, objects


# insertion conversation in database used API
def send_info_conversation(id_conv,tag,question,chaine,id_agent,user_infos, outputRate):
    x = round(outputRate)
    #outputRate = outputRate.strip()

    hed = {'Authorization': 'Token ff5f834b3cd8b2ba52f862998138d5b9b2c63dd7', 'Content-type': 'application/json'}

    #url = conf.URL+':8000/api/stats/{}/analytics/'.format(id_agent)
    url = conf.URL+':8000/api/stats/{}/analyticbyusers/'.format(id_agent)

    user_info=dict()
    user_info['first_name']=user_infos['first_name']
    user_info['last_name']=user_infos['last_name']
    user_info['gender']=user_infos['gender']
    user_info['client_id']=id_conv
    user_info['page_id']=user_infos['page_id']
    user_info['access_token']=user_infos['access_token']
    datatest = {
        "sessionID": id_conv,
        "chaine": chaine,
        "adresseIP": request.remote_addr,
        "country": geo.country_name_by_addr(str(request.remote_addr)),
        "platform": request.user_agent.platform,
        "browser": request.user_agent.browser,
        "agentStats":[
            {
        "inputMsg": question,
        "outputRate": str(outputRate),
        "intentName": tag
            }
        ]
    }
    user_info['sessions']=[]
    user_info['sessions'].append(datatest)
    response = requests.post(url,  json=user_info, headers=hed)



@application.route('/remove/<string:id>', methods=['GET'])
def remove(id):
    global day_pre
    rem_list = []
    try:

        if (id == "*"):
            t = time.time() // 60
            for key,value in model.session.items():
                if(abs(t - value) > conf.SESSION_DURATION):
                    rem_list.append(key)
            if(rem_list):
                for key in rem_list:
                    model.session.pop(key)
                    if key in model.context:
                        model.context.pop(key)
                    if key in model.entity:
                        model.entity.pop(key)
                    if key in model.require:
                        model.require.pop(key)
        else:
            del model.context[id]
            del model.session[id]
    except:
        print("id introuvable !!!")
    return  jsonify({"msg": "succefful"})


@application.route('/reply', methods=['POST'])
#@limiter.limit("1/3 second")
def get_reply():
    data = request.json
    id_conv = data["id"]
    chaine = data["chaine"]
    gender = data["user_infos"]["gender"]
    user_infos = data["user_infos"]
    id_agent = str(id_ag)
    question = data["question"]
    value = question
    question = question.lower()
    if (question != ""):
        # question = question.replace("'", " ")
        # value = question
        question = question.replace("-", " ")
        question = question.replace("?", "")
        question = question.replace("ç", "c")
        question = question.replace(",", "")
        question = question.replace("â", "a")

        # filter words
        question = filter_sentens(question)
        # corrector sentence
        question = str(correcter.correct_words(cheker, question, language))
        # transtate sentence
        print("question correct:" + question)

        # get default response from agent bot
        outputRate = 0
        tag, R1, obj = get_intents_default("e619abf36bd80410b3854c9573fdc63f94a5a942", gender)
        json = {"R1": R1}

        if value in [ "97b7c09ed472cd10882de674559282dcb7e5c471", "58108524103242b03af9d44b72dd6b6c9280072e 140ccda42adea5f48c8a617171f3f21d61f6454f"]:
            tag, R1, obj = get_intents_default(value,gender)
            json = {"R1": R1}
            send_info_conversation(id_conv, tag, value, chaine, id_agent,user_infos, outputRate)
            return jsonify({"msg": json, "objet": obj})
        if value == "a45ec879abd5879fd545ae545ccv6910ab3ffe59":
            tag, R1, obj = get_intents_default(value, gender)
            json = {"R1": R1}
            send_info_conversation(id_conv, tag, value, chaine, id_agent,user_infos, outputRate)
            return jsonify({"msg": json, "objet": obj})

        reply_0 = model.response( language,value,question, id_conv, gender, user_infos, show_details=False)
        if (reply_0):
            responses = str(reply_0[0])
            print("ahmed: ",responses)
            obj = reply_0[1]
            tag = reply_0[2]
            outputRate = reply_0[3]

            responses = responses.split("*")
            indice = 1
            for r in responses:
                r = r.strip()
                json["R" + str(indice)] = str(r)
                indice += 1
        if not (id_conv in model.entity):
            send_info_conversation(id_conv, tag, value, chaine, id_agent, user_infos, outputRate)
        return jsonify({"msg": json, "objet": obj})

@application.route('/check_status', methods=['POST', 'GET'])
def CheckStatus():
    return jsonify({"success": "ok"})

# if __name__ == '__main__':
#     # context = (cer, key)
#     # application.run(host='0.0.0.0',threaded=True,port=5003,ssl_context=context, debug = True
#     application.run(host='0.0.0.0', threaded=True, port=int(port), debug=True)
