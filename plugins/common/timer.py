#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:timer.py
# Date:Sun Jul 07 18:01:06 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import traceback
import time
import threading
import logging
LOG = logging.getLogger("plugins")


class Timer(threading.Thread):

    def __init__(self, target, args, interval):
        super(Timer, self).__init__()
        self.setDaemon(True)
        self.target = target
        self.args = args
        self.interval = interval
        self.thread_stop = False

    def __do(self):
        try:
            self.target(*self.args)
        except:
            LOG.error(traceback.print_exc())
            time.sleep(int(self.interval) * 5)

    def run(self):
        while not self.thread_stop:
            self.__do()
            time.sleep(int(self.interval))

    def stop(self):
        self.thread_stop = True
