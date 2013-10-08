#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:start_vt_manager.py
# Date:Mon Jul 08 15:48:11 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import os


def mklogdir():
    if not os.path.exists('logs'):
        os.mkdir('logs')
mklogdir()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ccf.settings")
import traceback
from twisted.internet import reactor
from twisted.web import server
from plugins.vt.statemanager import StateManager
from plugins.vt.vtmanager import VTManager
from etc import config
import logging
LOG = logging.getLogger("vt_manager")


def start_service():
    if config.vt_manager:
        service = server.Site(VTManager())
        reactor.listenTCP(config.vt_manager_port, service)
    try:
        reactor.run()
    except Exception:
        LOG.error(traceback.print_exc())


def start_statemanager():
    try:
        statemanager = StateManager()
        statemanager.start()
    except Exception:
        LOG.error(traceback.print_exc())


if __name__ == "__main__":
    start_statemanager()
    start_service()
