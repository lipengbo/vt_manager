#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:agentclient.py
# Date:Sat Oct 05 18:13:35 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from xmlrpcclient import get_rpc_client
from etc import config


class MonitorClient(object):
    def __init__(self, ip):
        self.client = get_rpc_client(ip, config.monitor_service_port)

    def get_domain_state(self, vname):
        return self.client.get_domain_state(vname)

    def get_host_info(self):
        return self.client.get_host_info("test")

    def get_host_status(self):
        return self.client.get_host_status("test")


class ComputeClient(object):
    def __init__(self, ip):
        self.client = get_rpc_client(ip, config.compute_service_port)

    def do_domain_action(self, vname, action):
        return self.client.do_domain_action(vname, action)

    def create_vm(self, vmInfo, netInfo):
        """
        vmInfo:
            {
                'name': name,
                'mem': mem,
                'cpus': cpus,
                'img': imageUUID,
                'mac': mac,
                'hdd': imageSize 2G,
                'dhcp': 1 or 0,
                'glanceURL': glanceURL,
                'type':0/1/2 0 controller 1 slice 2 gateway
            }
        netInfo:
            {
                'ip': address,
                'netmask': netmask,
                'broadcast': broadcast,
                'gateway': gateway,
                'dns': dns,
            }
        """
        return self.client.create_vm(vmInfo, netInfo)

    def delete_vm(self, vname, vm_ip):
        return self.client.delete_vm(vname, vm_ip)
