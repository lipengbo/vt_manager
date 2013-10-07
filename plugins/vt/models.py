from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from resources.models import IslandResource, Server
from slice.models import Slice
from plugins.ipam.models import IPUsage
from plugins.common import utils
from django.utils.translation import ugettext as _
DOMAIN_STATE_TUPLE = (
    (0, _('nostate')),
    (1, _('running')),
    (2, _('blocked')),
    (3, _('paused')),
    (4, _('shutdown')),
    (5, _('shutoff')),
    (6, _('crashed')),
    (7, _('pmsuspended')),
    (8, _('building')),
    (9, _('failed')),
    (10, _('not exist'))
)
DOMAIN_STATE_DIC = {
    'nostate': 0,
    "running": 1,
    "blocked": 2,
    "paused": 3,
    "shutdown": 4,
    "shutoff": 5,
    "crashed": 6,
    "pmsuspended": 7,
    "building": 8,
    "failed": 9,
    "notexist": 10,
}
HOST_STATE = {
    'active': 1,
    'disactive': 0,
}
VM_TYPE = (
    (0, _('vm for controller')),
    (1, _('vm for slice')),
    (2, _('vm for gateway'))
)


class Image(models.Model):
    uuid = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=36)
    url = models.CharField(max_length=256)
    type = models.IntegerField(null=True)
    version = models.CharField(null=True, max_length=32)

    def __unicode__(self):
        return self.name


class Flavor(models.Model):
    name = models.CharField(max_length=64)
    cpu = models.IntegerField()
    ram = models.IntegerField()
    hdd = models.IntegerField()

    def __unicode__(self):
        return self.name


class VirtualMachine(IslandResource):
    uuid = models.CharField(max_length=20, null=True, unique=True)
    ip = models.ForeignKey(IPUsage, null=True)
    mac = models.CharField(max_length=20, null=True)
    enable_dhcp = models.BooleanField(default=True)
    vnc_port = models.IntegerField(null=True)
    slice = models.ForeignKey(Slice)
    flavor = models.ForeignKey(Flavor)
    image = models.ForeignKey(Image)
    server = models.ForeignKey(Server)
    state = models.IntegerField(null=True, choices=DOMAIN_STATE_TUPLE)
    type = models.IntegerField(null=False, choices=VM_TYPE)

    def get_ipaddr(self):
        return self.ip.ipaddr

    def get_netmask(self):
        return str(self.ip.supernet.get_network().netmask)

    def get_network(self):
        return str(self.ip.supernet.get_network().network)

    def get_ip_range_size(self):
        return self.ip.supernet.get_network().size

    def get_prefixlen(self):
        return self.ip.supernet.get_network().prefixlen

    def get_cidr(self):
        return str(self.ip.supernet.get_network().cidr)

    def get_broadcast(self):
        return str(self.ip.supernet.get_network().broadcast)

    def get_slice_id(self):
        return self.slice.id

    def get_image_uuid(self):
        return self.image.uuid

    def get_image_name(self):
        return self.image.name

    def get_image_url(self):
        return self.image.url

    def create_vm(self):
        print '----------------------create a vm=%s -------------------------' % self.name

    def delete_vm(self):
        print '----------------------delete a vm=%s -------------------------' % self.name

    def do_action(self, action):
        print '----------------------vm action=%s-------------------------' % action


class HostMac(models.Model):
    mac = models.CharField(max_length=32)
    host_type = models.ForeignKey(ContentType)
    host_id = models.PositiveIntegerField()
    #: the switch that the rule is applied on, can be Switch or VirtualSwitch
    host = generic.GenericForeignKey('host_type', 'host_id')


@receiver(pre_save, sender=VirtualMachine)
def vm_pre_save(sender, instance, **kwargs):
    if not instance.ip:
        instance.ip = IPUsage.objects.allocate_ip(instance.slice.name)
    if not instance.uuid:
        instance.uuid = utils.gen_uuid()
    if not instance.mac:
        instance.mac = utils.generate_mac_address(instance.get_ipaddr())
    if not instance.vnc_port:
        instance.vnc_port = 5900 + VirtualMachine.objects.filter(server=instance.server).count()
    if not instance.state:
        instance.state = DOMAIN_STATE_DIC['building']


@receiver(post_save, sender=VirtualMachine)
def vm_post_save(sender, instance, **kwargs):
    if kwargs.get('created'):
        instance.create_vm()


@receiver(pre_delete, sender=VirtualMachine)
def vm_pre_delete(sender, instance, **kwargs):
    instance.delete_vm()


@receiver(post_delete, sender=VirtualMachine)
def vm_post_delete(sender, instance, **kwargs):
    IPUsage.objects.release_ip(instance.ip)
