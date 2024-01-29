#
import psutil
import time
import time
import psutil
import requests
import subprocess
#
# def checkIfProcessRunning(processName):
#     '''
#     Check if there is any running process that contains the given name processName.
#     '''
#     for proc in psutil.process_iter():
#         x=None
#         try:
#
#             x = [x for x in proc.cmdline() if processName in x.split("/")]
#             if x:
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#     return False
#
#
# def stop_if_already_running():
#     script_path = "agent_recovery.py"
#     v= checkIfProcessRunning(script_path)
#     return v
#
# print(stop_if_already_running())
#
# for i in range(0,10):
#     print(i)
#     time.sleep(5)


# def send_failaid_notification():
# Send Email when script is complete
import smtplib

a=True
SERVER = "smtp.ionos.com"
FROM = "technique@ritabot.io"
TO = ["hajjej.abdelmonom@gmail.com", "abdelmonom.hajjej@solixy.com"]
server = smtplib.SMTP(SERVER)
if True:
    print("hello")

    SUBJECT = "The Script Has Completed"
    #MSG = "This is an auto generated Message.\n\rThe Reconcile & Compress script has completed.\n\n"
    MSG = "Bonjour, \n\r L'agent [nom: {}, id: {}] s'arrêter de fonctionner d'une' façon inattendue" \
              "\n\r Nous avons essayer de le relancer encore une fois \n\r" \
              "Pour tester l'etat actuel de cet agent, vous pouvez consulter le lien en ci-dessous \n\r" \
              "https://dev.ritabot.io:{}/reply/100&0&web&salem"
    # Prepare actual message
    MESSAGE = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (FROM, ", ".join(TO), SUBJECT, MSG.encode("utf8"))

    # Send the mail
    from email.message import EmailMessage
    msg=EmailMessage()
    agent=dict()
    agent['name'] ="hajjej"
    MSG = r"Hello, this is a test message {}".format(agent['name'])
    msg.set_content(MSG)

    msg['Subject'] = f'Hello'
    msg['From'] = FROM
    msg['To'] = TO

    server.login(FROM, 'W7jryzp{Y9xD]*W')
    #server.sendmail(msg)
    server.send_message(msg)

server.quit()