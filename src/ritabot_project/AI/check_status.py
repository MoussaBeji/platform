# -*- coding: utf-8 -*-
import sys
import smtplib
import requests
import conf
import subprocess

EMAIL_ADDRESS = conf.EMAIL_ADDRESS
EMAIL_PASSWORD = conf.EMAIL_PASSWORD
RECEIVER_ADDRESS = conf.RECEIVER_ADDRESS


class Check_Status_Services():

    def __init__(self, port, name_service):

        self.url = conf.URL
        self.port = port
        self.name_service = name_service

    def notify_user(self):

        server = smtplib.SMTP('smtp.solixy.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = 'YOUR ' + self.name_service + ' IS DOWN ON DEV!'
        body = 'Make sure the service restarted and it is back up'
        msg = f'Subject: {subject}\n\n{body}'
        server.sendmail(EMAIL_ADDRESS, RECEIVER_ADDRESS, msg)
        print('message successfuly sent')
        server.quit()


    def reboot_service(self):

        cmd ="sudo service " + self.name_service + " restart"
        print(cmd)
        subprocess.Popen([cmd], shell=True)

    def check(self):

        try:
            if(int(self.port) == 8000):
                url = self.url + ":" + str(self.port) + "/api/check_status/"
            else:
                url = self.url + ":" + str(self.port) + "/check_status"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                #self.notify_user()
                self.reboot_service()
            else:
                pass
        except Exception as e:
            #self.notify_user()
            self.reboot_service()


port = str(sys.argv[1])
name_service = str(sys.argv[2])

check = Check_Status_Services(port, name_service)
check.check()
