from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from resources.models import Resource, Server, IslandResource
from slice.models import Slice


class Gateway(Server):
    pass
