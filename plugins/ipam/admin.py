#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:admin.py
# Date:Fri Sep 20 16:24:06 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.contrib import admin
from models import Network, Subnet, IPUsage
from forms import NetworkForm, SubnetForm, IPUsageForm


class NetworkAdmin(admin.ModelAdmin):

    model = Network
    form = NetworkForm


class SubnetAdmin(admin.ModelAdmin):

    model = Subnet
    form = SubnetForm
    list_display = ("supernet", "netaddr", "owner", "is_owned", "is_used", "size", "update_time")


class IPUsageAdmin(admin.ModelAdmin):

    model = IPUsage
    form = IPUsageForm


admin.site.register(Network, NetworkAdmin)
admin.site.register(Subnet, SubnetAdmin)
admin.site.register(IPUsage, IPUsageAdmin)
