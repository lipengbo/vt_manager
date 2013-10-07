"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from plugins.openflow.controller_api import slice_add_controller, slice_change_controller
from plugins.openflow.models import FlowSpaceRule
from plugins.openflow.flowvisor_api import flowvisor_add_slice, flowvisor_del_slice
from project.models import Project
from plugins.openflow.flowspace_api import create_default_flowspace, flowspace_nw_add
from slice.slice_api import create_slice_api


class ControllerTest(TestCase):
    fixtures = ['cjxunittest.json']

    def test_slice_add_controller(self):
        print 'test_slice_add_controller'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            slice_add_controller(slice_obj, island.controller_set.all()[0])
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            if slice_obj.controller_set.all().count() == 1:
                self.assertTrue(True)
            else:
                self.assertFalse(True)

    def test_slice_change_controller(self):
        print 'test_slice_change_controller'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            slice_add_controller(slice_obj, island.controller_set.all()[0])
            flowvisor_add_slice(island.flowvisor_set.all()[0], slice_obj.name,
                slice_obj.get_controller(), slice_obj.owner.email)
            slice_change_controller(slice_obj, '192.168.5.104', '6565')
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            controllers = slice_obj.controller_set.all()
            if controllers.count() == 1 and controllers[0].ip == '192.168.5.104' and controllers[0].port == 6565:
                self.assertTrue(True)
            else:
                self.assertFalse(True)


class FlowvisorTest(TestCase):
    fixtures = ['cjxunittest.json']

    def test_flowvisor_add_slice(self):
        print 'test_flowvisor_add_slice'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            slice_add_controller(slice_obj, island.controller_set.all()[0])
            flowvisor_add_slice(island.flowvisor_set.all()[0], slice_obj.name,
                slice_obj.get_controller(), slice_obj.owner.email)
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertTrue(True)

    def test_flowvisor_del_slice(self):
        print 'test_flowvisor_del_slice'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            slice_add_controller(slice_obj, island.controller_set.all()[0])
            flowvisor_add_slice(island.flowvisor_set.all()[0], slice_obj.name,
                slice_obj.get_controller(), slice_obj.owner.email)
            flowvisor_del_slice(slice_obj.get_flowvisor(), slice_obj.name)
        except Exception, ex:
            print ex
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertFalse(True)
        else:
            flowvisor_del_slice(island.flowvisor_set.all()[0], 'cjxunittestslice')
            self.assertTrue(True)


class FlowspaceTest(TestCase):
    fixtures = ['cjxunittest.json']

    def test_create_default_flowspace(self):
        print 'test_create_default_flowspace'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        slice_obj = create_slice_api(project,
            'cjxunittestslice', 'description',
            island, project.owner)
        flowspace_obj = create_default_flowspace(slice_obj, 'test1', 100, 1,
            '', '', '', '', '', '', '', '', '', '', '')
        self.assertTrue(flowspace_obj.id)

    def test_flowspace_nw_add(self):
        print 'test_create_default_flowspace'
        project = Project.objects.all()[0]
        island = project.islands.all()[0]
        old_nws = ['192.168.5.37/24', '192.168.5.38/24']
        new_nm = '192.168.5.35/24'
        try:
            slice_obj = create_slice_api(project,
                'cjxunittestslice', 'description',
                island, project.owner)
            flowspace_nw_add(slice_obj, old_nws, new_nm)
        except Exception, ex:
            print ex
            self.assertFalse(True)
        else:
            if FlowSpaceRule.objects.all().count() == 6:
                self.assertTrue(True)
            else:
                self.assertFalse(True)
