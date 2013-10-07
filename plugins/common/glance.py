#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:glance.py
# Date:Tue Jul 09 02:36:49 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import utils
from etc import config


def get_image_list():
    glance_url = config.generate_glance_url()
    index_url = glance_url + '/images'
    try:
        images = utils.execute(['curl', index_url])
    except:
        #Try it again
        images = utils.execute(['curl', index_url])
    images = "images=" + images
    exec(images)
    for image in images['images']:
        download_url = glance_url + '/image/' + image['id']
        yield image['id'], image['name'], download_url
