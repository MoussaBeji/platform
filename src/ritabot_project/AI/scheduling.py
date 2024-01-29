# -*- coding: utf-8 -*-
import conf
from crontab import CronTab


class Scheduling():
    # get username system
    username = conf.NAME_USER
    my_cron = CronTab(user=username)

    def __init__(self, port, name_service, command):

        self.name_service = name_service
        self.port = port
        self.command = command

    def launch(self):

        self.remove_crontab()
        # create a job
        job = self.my_cron.new(command = self.command , comment='Crontab_' + self.name_service)
        job.minute.every(1)
        self.my_cron.write()


    def remove_crontab(self):

        # Clearing Jobs that its clear_context name From Crontab
        for job in self.my_cron:
            if job.comment == 'Crontab_' + self.name_service:
                self.my_cron.remove(job)
                self.my_cron.write()

    def get_list_job(self):
        # show all jobs
        for job in self.my_cron:
            print(job)

