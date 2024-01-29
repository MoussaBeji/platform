import os
import json
import time
import psutil
import requests
import subprocess
import smtplib
from email.message import EmailMessage
#sudo service cron restart after each change
training_path = "/var/lib/jenkins/workspace/ritabot/src/ritabot_project/AI/"
#pip install psutil

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    y=[]
    for proc in psutil.process_iter():
        x=None
        try:

            x = [x for x in proc.cmdline() if processName in x.split("/")]
            if x:
                print(proc, '   ', proc.pid)
                print(x)
                y.append(x)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if len(y)>1:
        return True
    else:
        return False

def getagentsinfo():
    req=None
    hed = {'Authorization': 'Token ff5f834b3cd8b2ba52f862998138d5b9b2c63dd7', 'Content-type': 'application/json'}
    url = 'https://dev.ritabot.io:8000/api/bot/agentinformations/'
    try:
        req = requests.get(url=url,params=None, headers=hed, timeout=20)
    except:
        raise Exception("timeout acheived")

    if req.status_code != 200:
        raise Exception('We can not got informations about agents')

    req.encoding = 'utf-8'
    resp=req.json().copy()
    list=[agentinfo for agentinfo in resp if agentinfo['status']=='En marche']
    return list

def gettrainedagentsinfo():
    req=None
    hed = {'Authorization': 'Token ff5f834b3cd8b2ba52f862998138d5b9b2c63dd7', 'Content-type': 'application/json'}
    url = 'https://dev.ritabot.io:8000/api/bot/agentinformations/'
    try:
        req = requests.get(url=url,params=None, headers=hed, timeout=20)
    except:
        raise Exception("timeout acheived")

    if req.status_code != 200:
        raise Exception('We can not got informations about agents')

    req.encoding = 'utf-8'
    resp=req.json().copy()
    list=[agentinfo for agentinfo in resp if agentinfo['status']=='entrainer']
    return list

def tetstagentstatus(agent):
    try:
        req = requests.get(url='https://dev.ritabot.io:{}/reply/100&0&web&salem'.format(agent['port']), params=None, timeout=60)
    except:
        print("Agent (name: {}, ID:{}) is down".format(agent['name'], agent['id']))
        print('URL for Testing: https://dev.ritabot.io:{}/reply/100&0&web&salem'.format(agent['port']))
        return False

    if req.status_code == 200:
        print ("Agent (name: {}, ID:{}) works fine".format(agent['name'], agent['id']))
        print('URL for Testing: https://dev.ritabot.io:{}/reply/100&0&web&salem'.format(agent['port']))
        return True
    #
    else:
        print("Agent (name: {}, ID:{}) is down".format(agent['name'], agent['id']))
        print('URL for Testing: https://dev.ritabot.io:{}/reply/100&0&web&salem'.format(agent['port']))
        return False




def launchTraining(agentID):
    req=None
    hed = {'Authorization': 'Token ff5f834b3cd8b2ba52f862998138d5b9b2c63dd7', 'Content-type': 'application/json'}
    url1 = 'https://dev.ritabot.io:8000/api/bot/launch_training'
    url = 'https://dev.ritabot.io:8000/api/bot/test_training'

    datatest = {'agent_id':agentID}
    try:
        response1 = requests.post(url1, json=datatest, headers=hed)


        x=None
        i=0
        while not x and i<10:
            agent_list = gettrainedagentsinfo()
            # print("status", x['status'])
            print("step", i)
            x=[x for x in agent_list if x['id'] == agentID]
            i+=1
            if not x:
                time.sleep(15)




        response = requests.post(url, json=datatest, headers=hed)
    except:
        pass
    return True


############---------------SEND EMAIL FUNCTION-------------------##############################
def sendmail(agent, msg, subject):
    pass
    print("send mail")
    SERVER = "smtp.ionos.com"
    FROM = "technique@ritabot.io"
    TO = ["technique@ritabot.io"]
    MSG = msg

    server = smtplib.SMTP(SERVER)
    server.login(FROM, 'W7jryzp{Y9xD]*W')
    msg = EmailMessage()
    msg.set_content(MSG)

    msg['Subject'] = subject
    msg['From'] = FROM
    msg['To'] = TO

    #server.sendmail(FROM, TO, MESSAGE)
    server.send_message(msg)
    server.quit()

############----------------------------------##############################


script_path = "agent_recovery.py"
verif= checkIfProcessRunning(script_path)

if not verif:
    agent_list=getagentsinfo()
    for agent in agent_list:
        # print(agent)
        status=tetstagentstatus(agent)
        if not status:
            try:
                print('close port', agent['port'])
                cmd = "sudo fuser -k -n tcp " + str(agent['port'])
                subprocess.Popen(cmd.split())

            except:
                pass

            # try:
            print('launch agent -- ID: {} -- name {}'.format(agent['id'], agent['name']))

#r"Informations about the current stat of Agent {}".format(agent['name']) // r"This is an auto generated Message.The Reconcile & Compress script has completed {}".format(agentt['name'])
            launchTraining(agent['id'])
            status = tetstagentstatus(agent)
            if not status:
                # We can not restart the agent***
                subject = r"L'agent {} est interrompu".format(agent['name'])
                msg = f"Le relancement automatique de l'agent {agent['name']} est effectué avec succès.\n\r" \
                      f" Veillez le tester manullement à travers le lien là dessous: \n\r" \
                      f"https://dev.ritabot.io:{agent['port']}/reply/100&0&web&salem"
                sendmail(agent, msg, subject)
            else:
                # the considered agent was succefuly restarted
                subject = r"L'agent {} a été relancé avec succés".format(agent['name'])
                msg = f"L'interruption de l'agent {agent['name']} a été récupéré avec succes.\n\r" \
                      f" Veillez le tester manullement à travers le lien là dessous: \n\r" \
                      f"https://dev.ritabot.io:{agent['port']}/reply/100&0&web&salem"
                sendmail(agent, msg, subject)

        else:
            pass
