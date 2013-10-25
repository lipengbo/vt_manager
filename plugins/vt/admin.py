#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:admin.py
# Date:Mon Sep 23 13:18:05 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.contrib import admin
from models import VirtualMachine, HostMac, Flavor, Image
from django import forms


class VmAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(VmAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = VirtualMachine
        fields = ("name", "slice", "island", "flavor", "image", "server", "enable_dhcp", "type", 'state')


class VirtualMachineAdmin(admin.ModelAdmin):

    model = VirtualMachine
    form = VmAdminForm
    list_display = ("name", "slice", "island", "flavor", "image", "server", "enable_dhcp", "type", 'state')


admin.site.register(VirtualMachine, VirtualMachineAdmin)
admin.site.register(HostMac)
admin.site.register(Flavor)
admin.site.register(Image)
