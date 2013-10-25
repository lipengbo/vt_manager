#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:api.py
# Date:Sat Oct 05 00:10:59 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from plugins.vt.models import VirtualMachine, Image, Flavor
from plugins.ipam.models import IPUsage
from etc.config import default_flavor_id
from plugins.common.vt_manager_client import VTClient
from resources.models import Server
from etc.config import function_test


def create_vm_for_controller(island_obj, slice_obj, image_name):
    ip_obj = IPUsage.objects.allocate_ip_for_controller()
    vm = VirtualMachine(slice=slice_obj, island=island_obj, ip=ip_obj)
    vm.name = image_name
    images = Image.objects.filter(name=image_name)
    if images:
        vm.image = images[0]
    vm.flavor = Flavor.objects.get(id=default_flavor_id)
    if function_test:
        #hostlist = [switch.virtualswitch.server for switch in slice_obj.get_virtual_switches_server()]
        hostlist = Server.objects.all()
        vm.server = hostlist[0]
    else:
        #hostlist = [(switch.virtualswitch.server.id, switch.virtualswitch.server.ip) for switch in slice_obj.get_virtual_switches_server()]
        hostlist = [(server.id, server.ip) for server in Server.objects.all()]
        serverid = VTClient().schedul(vm.flavor.cpu, vm.flavor.ram, vm.flavor.hdd, hostlist)
        if not serverid:
            raise Exception('resource not enough')
        vm.server = Server.objects.get(id=serverid)
    vm.type = 0
    vm.save()
    return vm, str(ip_obj)


def delete_vm_for_controller(vm):
    vm.delete()
