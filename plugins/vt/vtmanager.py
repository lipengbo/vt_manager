#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:vtmanager.py
# Date:Sun Oct 06 01:40:50 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from plugins.common.agent_client import AgentClient
from resources.models import Server
from plugins.vt.models import VirtualMachine
from etc import config
import json


class Filter(object):

    def __init__(self, vcpu, mem, disk):
        self.mem = int(mem)
        self.disk = int(disk)
        self.vcpu = int(vcpu)

    def check_resource_by_monitor(self, hostid, hostip):
        client = AgentClient(hostip)
        host_status = json.loads(client.get_host_status())
        if config.unique_hosts_per_alloc <= client.get_instances_count():
            return False
        if self.vcpu > int(client.get_host_info()['vcpus']):
            return False
        if config.max_cpu < float(host_status['cpu']):
            return False
        mem_free = float(host_status['mem'][4])
        mem_total = float(host_status['mem'][0])
        if config.max_mem < (mem_total - mem_free - (self.mem << 20)) * 100 / mem_total:
            return False
        disk_free = int(host_status['disk'].items()[0][1][2])
        if config.max_disk > (disk_free >> 30) - self.disk:
            return False
        return hostid

    def filter(self, host_list):
        for hostid, hostip in host_list:
            host = Server.objects.get(id=hostid)
            if host.state and self.check_resource_by_monitor(hostid, hostip):
                return hostid
        return False


from twisted.web import xmlrpc


class VTManager(xmlrpc.XMLRPC):

    def __init__(self):
        xmlrpc.XMLRPC.__init__(self, allowNone=True)
        self.request = None

    def render(self, request):
        self.request = request
        return xmlrpc.XMLRPC.render(self, request)

    def xmlrpc_schedul(self, vcpu, mem, disk, hostlist):
        print '--------------------schedul------------------------------'
        print 'vcpu=%s' % vcpu
        print 'mem=%s' % mem
        print 'disk=%s' % disk
        print 'hostlist=%s' % hostlist
        print '--------------------schedul------------------------------'
        return Filter(vcpu, mem, disk).filter(hostlist)

    def xmlrpc_set_domain_state(self, vname, state):
        try:
            VirtualMachine.objects.filter(uuid=vname).update(state=state)
        except:
            pass
        finally:
            return True
