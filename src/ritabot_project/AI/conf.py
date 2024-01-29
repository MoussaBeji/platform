# -*- coding: utf-8 -*-

import os

NB_NEURONS = 20
ERROR_THRESHOLD = 0.15
NB_EPOCH_THRESHOLD = 500
NB_EPOCH = 2000
BATCH_SIZE = 8
PRECISION = 101
INGONRE_STOP_WORDS = {"about", "you", "how","quel","quels","quelle","quelles","comment","peut","peux"}
SESSION_DURATION = 30
URL = "https://dev.ritabot.io"
SERVER_NAME = "dev.ritabot.io"
PROJECT_ENV = "/opt/ritabot/ritabot_env/bin"

#PATH_PROJECT = os.getcwd()
PATH_PROJECT = "/opt/ritabot/src/ritabot_project/AI"
#if used django
#PATH_PROJECT = os.getcwd() + "/AI/"

NAME_USER = "ubuntu"
CMD_PYTHON = "python"

SSL_CERTIFICATE = "/etc/nginx/ssl/domain.crt"
SSL_CERTIFICATE_KEY = "/etc/nginx/ssl/domain.key"

#for check status and notify by email
EMAIL_ADDRESS="wiem.aboussaoud@solixy.com"
EMAIL_PASSWORD="l2KfptNPn8YP"
RECEIVER_ADDRESS="ahmed.massoued@solixy.com"
