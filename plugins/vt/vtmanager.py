#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:vtmanager.py
# Date:Sun Oct 06 01:40:50 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from plugins.common.agentclient import ComputeClient, MonitorClient
from plugins.vt.models import VirtualMachine
from resources.models import Server
from etc import config


class Filter(object):

    def __init__(self, vcpu, mem, disk):
        self.mem = int(mem)
        self.disk = int(disk)
        self.vcpu = int(vcpu)

    def check_resource_by_monitor(self, hostid, hostip):
        client = MonitorClient(hostip)
        host_status = client.get_host_status()
        if self.vcpu > int(client.get_host_info()['vcpus']):
            return False
        if config.max_cpu < float(host_status['cpu_percent']):
            return False
        mem_free = float(host_status['mem']['free'])
        mem_total = float(host_status['mem']['total'])
        if config.max_mem < (mem_total - mem_free - self.mem) / mem_total:
            return False
        disk_free = float(host_status['disk_free'])
        if config.max_disk > disk_free - self.disk:
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

    def xmlrpc_do_domain_action(self, hostip, vname, action):
        print '--------------------do domain action------------------------------'
        print 'hostip=%s' % hostip
        print 'vname=%s' % vname
        print 'action=%s' % action
        print '--------------------do domain action------------------------------'
        return ComputeClient(hostip).do_domain_action(vname, action)

    def xmlrpc_create_vm(self, hostip, vminfo, netinfo):
        print '--------------------create vm------------------------------'
        print 'hostip=%s' % hostip
        print 'vminfo=%s' % vminfo
        print 'netinfo=%s' % netinfo
        print '--------------------create vm------------------------------'
        return ComputeClient(hostip).create_vm(vminfo, netinfo)

    def xmlrpc_delete_vm(self, hostip, vname):
        print '====================delete vm------------------------------'
        print 'hostip=%s' % hostip
        print 'vname=%s' % vname
        print '--------------------delete vm------------------------------'
        return ComputeClient(hostip).delete_vm(vname)

    def xmlrpc_set_domain_state(self, vname, state):
        VirtualMachine.objects.filter(uuid=vname).update(state=state)
        return True

    def xmlrpc_get_host_info(self, hostip):
        print '--------------------get host info------------------------------'
        print 'hostip=%s' % hostip
        print '--------------------get host info------------------------------'
        return MonitorClient(hostip).get_host_info()
