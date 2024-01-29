# -*- coding: utf-8 -*-
import conf
from crontab import CronTab

"""
this class allows you to create a crontab that checks
the status of the services (ritabot backend, api entity, webhook, api webview)
and relaunches them in case of failure
"""

services = {
    "scom_solaire": 7920,
    "ritabot": 8000,
    "api_entity": 5000,
    "webhook": 5001,
    "api_webview": 5002,
    "share_service": 5005
}


username = conf.NAME_USER
my_cron = CronTab(user=username)

def launch(command , name_service):
    my_cron = CronTab(user=username)
    remove_crontab()
    # create a job
    job = my_cron.new(command = command , comment='Crontab_ritabot')
    job.minute.every(1)
    my_cron.write()

def remove_crontab():

    # Clearing Jobs that its clear_context name From Crontab
    for job in my_cron:
        if job.comment == 'Crontab_ritabot':
            my_cron.remove(job)
            my_cron.write()

remove_crontab()
for name_service, port in services.items():
    command = conf.PROJECT_ENV + "/" + conf.CMD_PYTHON + ' ' + conf.PATH_PROJECT + '/check_status.py ' + str(port) + ' ' + name_service
    launch(command, name_service)

