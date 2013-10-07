"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from project.models import (Project, Category, Island)

class SimpleTest(TestCase):
    fixtures = ['users.json', 'islands.json',
            'cities.json', 'categories']

    def test_create_project(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
        self.assertTrue(project.id)
        self.assertTrue(project.memberships.count() == 1) #: there is a default member which is the owner
        self.assertTrue(project.memberships.all()[0] == owner)

    def test_create_category(self):
        category = Category(name="sdn2")
        category.save()
        self.assertTrue(category.id)

    def test_add_member_to_project(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
        self.assertTrue(project.memberships.count() == 1) #: there is a default member which is the owner
        project.add_member(User.objects.all()[1])
        self.assertTrue(project.memberships.count() == 2)

    def test_add_same_member_to_project(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
        self.assertTrue(project.memberships.count() == 1)
        project.add_member(User.objects.all()[1])
        self.assertTrue(project.memberships.count() == 2)
        project.add_member(User.objects.all()[1])
        self.assertTrue(project.memberships.count() == 2)

    def test_invite_member(self):
        owner = User.objects.all()[0]
        category = Category.objects.all()[0]
        project = Project(name="sdn project", owner=owner, category=category)
        project.save()
