#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:stateManager.py
# Date:Wed Jul 10 18:00:54 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import socket
from etc import config
from plugins.common import timer
from plugins.common.agent_client import AgentClient
from resources.models import Server
from plugins.vt.models import DOMAIN_STATE_DIC as DOMAIN_STATE, HOST_STATE


class StateManager(object):

    def start(self):
        t1 = timer.Timer(self.update_state, (), config.duration)
        t1.start()

    def update_state(self):
        for host_id, host_ip, state in self.__get_hosts_state():
            self.__update_host_state(host_id, state)
            if state == HOST_STATE['active']:
                self.__update_domain_state(host_id, host_ip)

    def __update_host_state(self, host_id, host_state):
        Server.objects.filter(id=host_id).update(state=host_state)

    def __update_domain_state(self, host_id, host_ip):
        server = Server.objects.get(id=host_id)
        for domain in server.virtualmachine_set.all():
            if domain.state in [DOMAIN_STATE['failed'], DOMAIN_STATE['building']]:
                continue
            domain.state = AgentClient(host_ip).get_domain_state(domain.uuid)
            domain.save()

    def __get_hosts_state(self):
        for host_id, host_ip, port in self.__get_hosts_id_ip_port_type():
            state = self.__get_host_state(host_ip, port)
            yield host_id, host_ip, state

    def __get_host_state(self, ipaddr, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(config.state_connection_timeout)
            s.connect((ipaddr, port))
            s.close()
            state = HOST_STATE['active']
        except:
            state = HOST_STATE['disactive']
        return state

    def __get_hosts_id_ip_port_type(self):
        hosts = Server.objects.all()
        for host in hosts:
            port = config.compute_service_port
            yield host.id, host.ip, port
