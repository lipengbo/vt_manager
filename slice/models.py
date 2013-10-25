from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.db.models import F
from django.dispatch import receiver

from project.models import Project, Island
from plugins.ipam.models import Subnet

SLICE_STATE_STOPPED = 0
SLICE_STATE_STARTED = 1
SLICE_STATES = (
        (SLICE_STATE_STOPPED, 'stopped'),
        (SLICE_STATE_STARTED, 'started'),
)
# Create your models here.


class Slice(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    project = models.ForeignKey(Project)
    date_created = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField()
    state = models.IntegerField(choices=SLICE_STATES,
            default=SLICE_STATE_STOPPED)
#     expired = models.IntegerField(default=0)

    islands = models.ManyToManyField(Island, through="SliceIsland")

    def add_island(self, island):
        SliceIsland.objects.get_or_create(
            island=island, slice=self)

    def change_description(self, description):
        self.description = description
        self.save()

    def add_resource(self, resource):
        resource.on_add_into_slice(self)

    def remove_resource(self, resource):
        resource.on_remove_from_slice(self)

    def stop(self):
        self.state = SLICE_STATE_STOPPED
        self.save()

    def start(self):
        self.state = SLICE_STATE_STARTED
        self.save()

    def get_flowvisor(self):
        flowvisors = self.flowvisor_set.all()
        if flowvisors:
            return flowvisors[0]
        else:
            return None

    def get_controller(self):
        controllers = self.controller_set.all()
        if controllers:
            return controllers[0]
        else:
            return None

    def get_island(self):
        islands = self.islands.all()
        if islands:
            return islands[0]
        else:
            return None

    def get_switches(self):
        return self.switch_set.all()

    def get_virtual_switches(self):
        from resources.models import VirtualSwitch
        switches = self.switch_set.all()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual():
                virtual_switches.append(switch.virtualswitch)
        print virtual_switches
        return virtual_switches

    def get_virtual_switches_gre(self):
        from resources.models import VirtualSwitch
        switches = self.switch_set.all()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual() and switch.has_gre_tunnel:
                virtual_switches.append(switch.virtualswitch)
        return virtual_switches

    def get_virtual_switches_server(self):
        from resources.models import VirtualSwitch
        switches = self.switch_set.all()
        virtual_switches = []
        for switch in switches:
            if switch.is_virtual() and not switch.has_gre_tunnel:
                virtual_switches.append(switch.virtualswitch)
        return virtual_switches

    def get_default_flowspaces(self):
        return self.flowspacerule_set.filter(is_default=1)

    def get_switch_ports(self):
        return self.switchport_set.all()

    def get_vms(self):
        return self.virtualmachine_set.all()

    def get_common_vms(self):
        return self.virtualmachine_set.filter(type=1)

    def get_nws(self):
        default_flowspaces = self.flowspacerule_set.filter(is_default=1, dl_type='0x800')
        nws = []
        for default_flowspace in default_flowspaces:
            if default_flowspace.nw_src != '' and default_flowspace.nw_src == default_flowspace.nw_dst:
                nws.append(default_flowspace.nw_dst)
        return nws

    def get_nw(self):
        try:
            nw_obj = Subnet.objects.get(owner=self.name)
            return nw_obj.netaddr
        except:
            return None

    def get_gws(self):
        default_flowspaces = self.flowspacerule_set.filter(is_default=1, dl_type='0x800')
        gws = []
        for default_flowspace in default_flowspaces:
            if default_flowspace.dl_src != '':
                gws.append(default_flowspace.dl_src)
        return gws

    def get_dhcp_vm_macs(self):
        default_flowspaces = self.flowspacerule_set.filter(is_default=1, dl_type='')
        dhcp_vm_macs = []
        for default_flowspace in default_flowspaces:
            if default_flowspace.dl_src != '':
                dhcp_vm_macs.append(default_flowspace.dl_src)
        return dhcp_vm_macs

    def get_show_name(self):
        slice_names = self.name.split('_')
        if len(slice_names) > 1:
            del slice_names[-1]
        return ('_').join(slice_names)

    def __unicode__(self):
        return self.name


class SliceIsland(models.Model):
    slice = models.ForeignKey(Slice)
    island = models.ForeignKey(Island)

    class Meta:
        unique_together = (("slice", "island"), )
        
@receiver(pre_delete, sender=Slice)
def pre_delete_slice(sender, instance, **kwargs):
    from slice.slice_api import delete_slice_api
    delete_slice_api(instance)
