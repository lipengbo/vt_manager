#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:forms.py
# Date:Mon Sep 23 13:26:45 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django import forms
from models import VirtualMachine


class VmForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(VmForm, self).__init__(*args, **kwargs)

    class Meta:
        model = VirtualMachine
        fields = ("name", "flavor", "image", "server", "enable_dhcp")
        widgets = {
            "flavor": forms.Select(attrs={'onblur': "check_vminfo()"}),
            "image": forms.Select(attrs={'onblur': "check_vminfo()"}),
            "server": forms.Select(attrs={'onblur': "check_vminfo()"}),
        }
