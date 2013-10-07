"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from slice.slice_api import create_slice_api, slice_change_description,\
    delete_slice_api, start_slice_api, stop_slice_api,\
    update_slice_virtual_network, get_slice_topology
from django.contrib.auth.models import User
from project.models import Project, Island
from resources.models import SwitchPort
from slice.models import *
from plugins.openflow.flowvisor_api import flowvisor_del_slice, flowvisor_add_slice
from plugins.openflow.flowspace_api import flowspace_nw_add
from plugins.openflow.controller import slice_add_controller
from resources.ovs_api import slice_add_ovs_ports


class SimpleTest(TestCase):
    fixtures = ['cjxunittest.json']

    def test_create_slice_step(self):
        print 'test_create_slice_step'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice(project,
                'cjxunittestslice', 'description',
                island, project.owner,
                ovs_ports, island.controller_set.all()[0])
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertTrue(slice_obj.id)

    def test_create_slice_api(self):
        print 'test_create_slice_api'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        try:
            slice_obj = create_slice_api(project, 'cjxunittestslice',
                'description', island, project.owner)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            self.assertTrue(slice_obj.id)

    def test_slice_change_description(self):
        print 'test_slice_change_description'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        try:
            slice_obj = create_slice_api(project, 'cjxunittestslice',
                'description', island, project.owner)
            slice_change_description(slice_obj, 'new_description')
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            self.assertEqual('new_description', slice_obj.description)

    def test_delete_slice_api(self):
        print 'test_delete_slice_api'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice(project,
                'cjxunittestslice', 'description',
                island, project.owner,
                ovs_ports, island.controller_set.all()[0])
            delete_slice_api(slice_obj)
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            if not Slice.objects.filter(name='cjxunittestslice'):
                self.assertTrue(True)
            else:
                flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
                self.assertFalse(True)

    def test_start_slice_api(self):
        print 'test_start_slice_api'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice(project,
                'cjxunittestslice', 'description',
                island, project.owner,
                ovs_ports, island.controller_set.all()[0])
            start_slice_api(slice_obj)
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertEqual(SLICE_STATE_STARTED, slice_obj.state)

    def test_stop_slice_api(self):
        print 'test_stop_slice_api'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice(project,
                'cjxunittestslice', 'description',
                island, project.owner,
                ovs_ports, island.controller_set.all()[0])
            start_slice_api(slice_obj)
            stop_slice_api(slice_obj)
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertEqual(SLICE_STATE_STOPPED, slice_obj.state)

    def test_update_slice_virtual_network(self):
        print 'test_update_slice_virtual_network'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice(project,
                'cjxunittestslice', 'description',
                island, project.owner,
                ovs_ports, island.controller_set.all()[0])
            flowspace_nw_add(slice_obj, [], '192.168.5.34/24')
            update_slice_virtual_network(slice_obj)
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertTrue(True)

    def test_get_slice_topology(self):
        print 'test_get_slice_topology'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice(project,
                'cjxunittestslice', 'description',
                island, project.owner,
                ovs_ports, island.controller_set.all()[0])
            topology = get_slice_topology(slice_obj)
            print topology
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertTrue(True)


def create_slice(project, name, description, island, user, ovs_ports, controller):
    slice_obj = None
    try:
        slice_obj = create_slice_api(project, name, description, island, user)
        slice_add_ovs_ports(slice_obj, ovs_ports)
        slice_add_controller(slice_obj, controller)
        flowvisor_add_slice(island.flowvisor_set.all()[0], name, slice_obj.get_controller(), user.email)
#         创建并添加网段
#         创建并添加网关
#         创建并添加dhcp
#         创建并添加虚拟机
        return slice_obj
    except:
        slice_obj.delete()
        raise
