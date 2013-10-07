#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:fields.py
# Date:Tue Oct 01 17:42:49 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.forms import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import netaddr


class IPField(forms.Field):

    invalid_format_error = _("Incorrect format for ip Address ")

    def __init__(self, *args, **kwargs):
        self.mask = kwargs.pop('mask', None)
        super(IPField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(IPField, self).validate(value)
        if not value and not self.required:
            return
        try:
            if self.mask:
                self.ip = netaddr.IPNetwork(value)
            else:
                self.ip = netaddr.IPAddress(value)
        except:
            raise ValidationError(self.invalid_format_error)

    def clean(self, value):
        super(IPField, self).clean(value)
        return str(getattr(self, 'ip', ''))
