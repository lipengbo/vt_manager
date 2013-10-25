"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from api import create_vm_for_controller
from slice.models import Slice
from project.models import Island
import json


class VMCreate(TestCase):
    fixtures = ['lpb_pemission.json', 'lpb_project_data.json', 'lpb_resource.json', 'lpb_image_data.json', 'lpb_unittest.json']

    def test_create_vm_for_controller(self):
        island_obj = Island.objects.get(id=1)
        slice_obj = Slice.objects.get(id=1)
        image_name = 'floodlight'
        vm = create_vm_for_controller(island_obj, slice_obj, image_name)
        self.assertTrue(vm)

    def test_create_vm_for_slice(self):
        context = {}
        context['name'] = 'vm1'
        context['flavor'] = 1
        context['image'] = 1
        context['server'] = 1
        context['enable_dhcp'] = True
        response = self.client.post(path='/plugins/vt/create/vm/1/', data=context)
        result = json.loads(response.content)
        self.assertTrue(result.get('result') == 0)
