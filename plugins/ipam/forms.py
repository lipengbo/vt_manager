#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:forms.py
# Date:Tue Oct 01 20:49:45 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django import forms
from models import Network, Subnet, IPUsage
from fields import IPField


class NetworkForm(forms.ModelForm):

    netaddr = IPField(mask=True)

    class Meta:
        model = Network


class SubnetForm(forms.ModelForm):

    netaddr = IPField(mask=True)

    class Meta:
        model = Subnet


class IPUsageForm(forms.ModelForm):

    ipaddr = IPField(mask=False)

    class Meta:
        model = IPUsage
