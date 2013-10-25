#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:tests.py
# Date:Sat Sep 21 21:51:43 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.test import TestCase
from plugins.ipam.models import IPUsage
from plugins.common.utils import timefunc
import time
import uuid


class Slice_subnet_test(TestCase):

    def setUp(self):
        print "------set up slice subnet test--------"
        for i in xrange(1, 11):
            self.create_subnet(owner=i)

    @timefunc
    def create_subnet(self, owner, ipcount=64):
        subnet = IPUsage.objects.create_subnet(owner=owner, timeout=5, ipcount=ipcount)
        self.assertTrue(subnet)
        return subnet

    @timefunc
    def allocate_ip(self, owner):
        ip = IPUsage.objects.allocate_ip(owner=owner)
        self.assertTrue('255.255.255.192' == str(ip.supernet.get_network().netmask))
        self.assertTrue(26 == ip.supernet.get_network().prefixlen)
        return ip

    @timefunc
    def release_ip(self, ip):
        result = IPUsage.objects.release_ip(ip=ip)
        self.assertTrue(result)

    @timefunc
    def delete_subnet(self, owner):
        result = IPUsage.objects.delete_subnet(owner=owner)
        self.assertTrue(result)

    def test_networkflow(self):
        for i in xrange(11, 21):
            self.create_subnet(owner=11)
            self.delete_subnet(owner=11)
        self.create_subnet(owner=11)
        IPUsage.objects.subnet_create_success(owner=11)
        ips = []
        for i in xrange(2):
            ip = self.allocate_ip(owner=11)
            print ip
            self.assertTrue(ip.ipaddr == '10.0.2.%s' % (129 + i))
            ips.append(ip)
        ip1 = self.allocate_ip(owner=11)
        self.assertTrue(ip1.ipaddr == '10.0.2.131')
        ip2 = self.allocate_ip(owner=11)
        self.assertTrue(ip2.ipaddr == '10.0.2.132')
        self.release_ip(ip1)
        ip1 = self.allocate_ip(owner=11)
        self.assertTrue(ip1.ipaddr == '10.0.2.131')
        for ip in ips:
            self.release_ip(ip)
        ip1 = self.allocate_ip(owner=11)
        self.assertTrue(ip1.ipaddr == '10.0.2.129')
        self.create_subnet(owner=12)
        self.delete_subnet(owner=11)
        sub13 = self.create_subnet(owner=13)
        self.assertTrue(sub13 == '10.0.2.128/26')
        time.sleep(5)
        sub14 = self.create_subnet(owner=14)
        self.assertTrue(sub14 == '10.0.0.0/26')

    def tearDown(self):
        print "------tear down slice subnet test--------"
        for i in xrange(2, 11):
            self.delete_subnet(owner=i)


class Subnet_test(TestCase):

    def setUp(self):
        print "------set up subnet test--------"

    def test_8(self):
        for i in xrange(32):
            sub = IPUsage.objects.create_subnet(owner=i + 1, timeout=120, ipcount=8)
            self.assertTrue(sub == '10.0.0.%s/29' % (i * 8))
        IPUsage.objects.delete_subnet(owner=31)
        sub = IPUsage.objects.create_subnet(owner=31, timeout=120, ipcount=16)
        self.assertTrue(sub)

    def test_16(self):
        for i in xrange(16):
            sub = IPUsage.objects.create_subnet(owner=i + 1, timeout=120, ipcount=16)
            self.assertTrue(sub == '10.0.0.%s/28' % (i * 16))
        for i in xrange(16):
            sub = IPUsage.objects.create_subnet(owner=i + 33, timeout=120, ipcount=16)
            self.assertTrue(sub == '10.0.1.%s/28' % (i * 16))

    def test_32(self):
        for i in xrange(8):
            sub = IPUsage.objects.create_subnet(owner=i + 1, timeout=120, ipcount=32)
            self.assertTrue(sub == '10.0.0.%s/27' % (i * 32))
        for i in xrange(8):
            sub = IPUsage.objects.create_subnet(owner=i + 33, timeout=120, ipcount=32)
            self.assertTrue(sub == '10.0.1.%s/27' % (i * 32))

    def test_64(self):
        for i in xrange(4):
            sub = IPUsage.objects.create_subnet(owner=i + 1, timeout=120, ipcount=64)
            self.assertTrue(sub == '10.0.0.%s/26' % (i * 64))
        for i in xrange(4):
            sub = IPUsage.objects.create_subnet(owner=i + 33, timeout=120, ipcount=64)
            self.assertTrue(sub == '10.0.1.%s/26' % (i * 64))

    @timefunc
    def create_subnet(self, owner, ipcount=64):
        subnet = IPUsage.objects.create_subnet(owner=owner, timeout=120, ipcount=ipcount)
        return subnet

    def test_networkflow(self):
        for i in xrange(100):
            sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=8)
            self.assertTrue(sub == '10.0.%s.%s/29' % (i, 0 * 64))
            sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=16)
            self.assertTrue(sub == '10.0.%s.%s/28' % (i, 1 * 64))
            sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=32)
            self.assertTrue(sub == '10.0.%s.%s/27' % (i, 2 * 64))
            sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=64)
            self.assertTrue(sub == '10.0.%s.%s/26' % (i, 3 * 64))
            for j in xrange(7):
                sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=8)
                self.assertTrue(sub == '10.0.%s.%s/29' % (i, (j + 1) * 8))
            for j in xrange(3):
                sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=16)
                self.assertTrue(sub == '10.0.%s.%s/28' % (i, 64 + (j + 1) * 16))
            sub = self.create_subnet(owner=str(uuid.uuid4()), ipcount=32)
            self.assertTrue(sub == '10.0.%s.160/27' % (i))

    def tearDown(self):
        print "------tear down subnet test--------"


class Phy_subnet_test(TestCase):

    def setUp(self):
        print "------set up physic subnet test--------"

    def test_test(self):
        ip1 = IPUsage.objects.allocate_ip_for_controller()
        self.assertTrue(ip1.ipaddr == '172.16.0.101')
        ip = IPUsage.objects.allocate_ip_for_controller()
        self.assertTrue(ip.ipaddr == '172.16.0.102')
        IPUsage.objects.release_ip_for_controller(ip1)
        ip1 = IPUsage.objects.allocate_ip_for_controller()
        self.assertTrue(ip1.ipaddr == '172.16.0.101')
        ip = IPUsage.objects.allocate_ip_for_controller()
        self.assertTrue(ip.ipaddr == '172.16.0.103')

    def tearDown(self):
        print "------tear down physic subnet test--------"
