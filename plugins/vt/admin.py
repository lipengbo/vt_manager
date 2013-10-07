#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:admin.py
# Date:Mon Sep 23 13:18:05 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.contrib import admin
from models import VirtualMachine, HostMac, Flavor, Image


admin.site.register(VirtualMachine)
admin.site.register(HostMac)
admin.site.register(Flavor)
admin.site.register(Image)
