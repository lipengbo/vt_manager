"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from resources.ovs_api import slice_add_ovs_ports, slice_change_ovs_ports, find_ovs_by_dpid, get_ovs_class
from slice.models import Slice
from slice.slice_api import create_slice_api
from resources.models import Switch, SwitchPort, VirtualSwitch
from project.models import Project


class SimpleTest(TestCase):
    fixtures = ['cjxunittest.json']

    def test_slice_add_ovs_ports(self):
        print 'test_slice_add_ovs_ports'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            slice_add_ovs_ports(slice_obj, ovs_ports)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            if slice_obj.switch_set.all().count() == 4 and slice_obj.switchport_set.all().count() == 6:
                self.assertTrue(True)
            else:
                self.assertFalse(True)

    def test_slice_change_ovs_ports(self):
        print 'test_slice_change_ovs_ports'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        ovs_ports = SwitchPort.objects.all()
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            slice_add_ovs_ports(slice_obj, ovs_ports)
            new_ovs_ports = []
            new_ovs_ports.append(ovs_ports[0])
            new_ovs_ports.append(ovs_ports[2])
            slice_change_ovs_ports(slice_obj, new_ovs_ports)
            new_ovs_ports = []
            new_ovs_ports.append(ovs_ports[1])
            new_ovs_ports.append(ovs_ports[3])
            new_ovs_ports.append(ovs_ports[2])
            slice_change_ovs_ports(slice_obj, new_ovs_ports)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            print slice_obj.switch_set.all()
            print slice_obj.switchport_set.all()
            if slice_obj.switch_set.all().count() == 2 and slice_obj.switchport_set.all().count() == 3:
                self.assertTrue(True)
            else:
                self.assertFalse(True)

    def test_find_ovs_by_dpid(self):
        print 'test_find_ovs_by_dpid'
        switches = Switch.objects.all()
        virtual_switches = VirtualSwitch.objects.all()
        for switch in switches:
            if find_ovs_by_dpid(switch.dpid).id != switch.id:
                self.assertFalse(True)
        for virtual_switch in virtual_switches:
            ovs = find_ovs_by_dpid(virtual_switch.dpid)
            print get_ovs_class(ovs)
            if ovs.id != virtual_switch.id:
                self.assertFalse(True)
        self.assertTrue(True)
