#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:management.py
# Date:Mon Sep 23 09:31:36 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from django.db.models.signals import post_syncdb
from django.dispatch import receiver
from plugins.common import glance
import models


@receiver(post_syncdb, sender=models)
def init_image(sender, **kwargs):
    if not models.Image.objects.all():
        for uuid, name, url in glance.get_image_list():
            image = models.Image(uuid=uuid, name=name, url=url)
            image.save()
