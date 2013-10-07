#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:models.py
# Date:Fri Sep 20 18:36:12 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext as _
from plugins.ipam import netaddr as na
import pytz
import datetime
import math


class IPManager(models.Manager):

    def create_subnet(self, owner, ipcount=64, timeout=120):
        supernet = Network.objects.get(type=1)
        subnets = Subnet.objects.filter(supernet=supernet, size=ipcount)
        unowned_sub = self.get_unowned_subnet(subnets, timeout)
        unused_sub = self.get_unused_subnet(subnets)
        if unowned_sub:
            new_sub = unowned_sub
        elif unused_sub:
            new_sub = unused_sub
        else:
            new_sub = self.get_new_subnet(owner, subnets, supernet, ipcount)
        new_sub.owner = owner
        new_sub.is_used = True
        new_sub.is_owned = False
        new_sub.save()
        return new_sub.netaddr

    def subnet_create_success(self, owner):
        subnet = Subnet.objects.get(owner=owner)
        subnet.is_owned = True
        subnet.save()
        return True

    def delete_subnet(self, owner):
        subnet = Subnet.objects.get(owner=owner)
        subnet.is_owned = False
        subnet.is_used = False
        subnet.save()
        return True

    def allocate_ip(self, owner):
        subnet = Subnet.objects.get(owner=owner, is_used=True, is_owned=True)
        ips = self.filter(supernet=subnet)
        unused_ips = ips.filter(is_used=False)
        if unused_ips:
            ip = unused_ips[0]
        else:
            ip_count = ips.count()
            subnet_network = subnet.get_network()
            new_ipaddr = subnet_network.get_host(ip_count)
            ip = IPUsage(supernet=subnet, ipaddr=str(new_ipaddr))
        ip.is_used = True
        ip.save()
        return ip

    def release_ip(self, ip):
        if ip:
            ip.is_used = False
            ip.save()
        return True

    def allocate_ip_for_controller(self):
        subnet = Subnet.objects.get(owner=0, is_used=True, is_owned=True)
        ips = self.filter(supernet=subnet)
        unused_ips = ips.filter(is_used=False)
        if unused_ips:
            ip = unused_ips[0]
        else:
            subnet_network = subnet.get_network()
            subnet_start = na.IPAddress(subnet.netaddr.partition('/')[0]).value - subnet_network.first
            ip_count = ips.count() + subnet_start
            new_ipaddr = subnet_network.get_host(ip_count)
            ip = IPUsage(supernet=subnet, ipaddr=str(new_ipaddr))
        ip.is_used = True
        ip.save()
        return ip

    def release_ip_for_controller(self, ip):
        return self.release_ip(ip)

    def get_unowned_subnet(self, subnets, timeout):
        unowned_subnets = subnets.filter(is_owned=False)
        for sub in unowned_subnets:
            if datetime.datetime.now(tz=pytz.UTC) >= sub.update_time + datetime.timedelta(seconds=timeout):
                return sub
        return False

    def get_unused_subnet(self, subnets):
        unused_subnets = subnets.filter(is_used=False)
        if unused_subnets:
            return unused_subnets[0]
        return False

    def get_new_subnet(self, owner, subnets, supernet, ipcount):
        if ipcount == 64:
            sub64_count = subnets.count()
            sub32_count = Subnet.objects.filter(supernet=supernet, size=32).count()
            sub16_count = Subnet.objects.filter(supernet=supernet, size=16).count()
            sub8_count = Subnet.objects.filter(supernet=supernet, size=8).count()
            sub32_count = math.ceil(sub32_count / 2.0)
            sub16_count = math.ceil(sub16_count / 4.0)
            sub8_count = math.ceil(sub8_count / 8.0)
            sub_count = int(sub64_count + sub32_count + sub16_count + sub8_count)
            new_subnet_addr = supernet.get_network().get_subnet(ipcount, sub_count)
        elif ipcount == 32:
            sub32_qs = subnets.order_by('-id')
            sub32_count = subnets.count()
            if sub32_count % 2:
                new_subnet_addr = sub32_qs[0].get_network().next()
            else:
                sub64_count = Subnet.objects.filter(supernet=supernet, size=64).count()
                sub16_count = Subnet.objects.filter(supernet=supernet, size=16).count()
                sub8_count = Subnet.objects.filter(supernet=supernet, size=8).count()
                sub32_count = math.ceil(sub32_count / 2.0)
                sub16_count = math.ceil(sub16_count / 4.0)
                sub8_count = math.ceil(sub8_count / 8.0)
                sub_count = int(sub64_count + sub32_count + sub16_count + sub8_count) << 1
                new_subnet_addr = supernet.get_network().get_subnet(ipcount, sub_count)
        elif ipcount == 16:
            sub16_qs = subnets.order_by('-id')
            sub16_count = subnets.count()
            if sub16_count % 4:
                new_subnet_addr = sub16_qs[0].get_network().next()
            else:
                sub64_count = Subnet.objects.filter(supernet=supernet, size=64).count()
                sub32_count = Subnet.objects.filter(supernet=supernet, size=32).count()
                sub8_count = Subnet.objects.filter(supernet=supernet, size=8).count()
                sub32_count = math.ceil(sub32_count / 2.0)
                sub16_count = math.ceil(sub16_count / 4.0)
                sub8_count = math.ceil(sub8_count / 8.0)
                sub_count = int(sub64_count + sub32_count + sub16_count + sub8_count) << 2
                new_subnet_addr = supernet.get_network().get_subnet(ipcount, sub_count)
        elif ipcount == 8:
            sub8_qs = subnets.order_by('-id')
            sub8_count = subnets.count()
            if sub8_count % 8:
                new_subnet_addr = sub8_qs[0].get_network().next()
            else:
                sub64_count = Subnet.objects.filter(supernet=supernet, size=64).count()
                sub32_count = Subnet.objects.filter(supernet=supernet, size=32).count()
                sub16_count = Subnet.objects.filter(supernet=supernet, size=16).count()
                sub32_count = math.ceil(sub32_count / 2.0)
                sub16_count = math.ceil(sub16_count / 4.0)
                sub8_count = math.ceil(sub8_count / 8.0)
                sub_count = int(sub64_count + sub32_count + sub16_count + sub8_count) << 3
                new_subnet_addr = supernet.get_network().get_subnet(ipcount, sub_count)
        new_subnet = Subnet(supernet=supernet, netaddr=str(new_subnet_addr), owner=owner)
        return new_subnet


class Network(models.Model):
    TYPE_CHOICE = ((0, _('subnet for phy')),
                  (1, _('subnet for slice')),)
    netaddr = models.CharField(max_length=20, null=False, unique=True)
    type = models.IntegerField(null=False, choices=TYPE_CHOICE)

    def get_network(self):
        return na.Network(self.netaddr)

    def __unicode__(self):
        return self.netaddr

    class Meta:
        ordering = ['id', ]


class Subnet(models.Model):
    supernet = models.ForeignKey(Network)
    netaddr = models.CharField(max_length=20, null=False, unique=True)
    owner = models.CharField(max_length=20, null=False, unique=True)
    is_owned = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    size = models.IntegerField()
    update_time = models.DateTimeField(auto_now=True)

    def get_network(self):
        return na.Network(self.netaddr)

    def __unicode__(self):
        return self.netaddr

    class Meta:
        ordering = ['id', ]


class IPUsage(models.Model):
    supernet = models.ForeignKey(Subnet)
    ipaddr = models.CharField(max_length=20, null=False, unique=True)
    is_used = models.BooleanField(default=False)
    objects = IPManager()

    def __unicode__(self):
        return self.ipaddr

    class Meta:
        ordering = ['id', ]


@receiver(post_save, sender=Network)
def create_base_subnet(sender, instance, **kwargs):
    network = instance
    if kwargs.get('created'):
        if network.type == 0:
            Subnet(supernet=network, netaddr=network.netaddr, owner=0, is_used=True, is_owned=True).save()


@receiver(pre_save, sender=Subnet)
def subnet_pre_save(sender, instance, **kwargs):
    instance.size = instance.get_network().size
