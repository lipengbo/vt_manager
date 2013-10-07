from django.contrib import admin

from project.models import (City, Island, Project, Category,
        Membership)
from slice.models import Slice
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch
from plugins.openflow.models import Flowvisor, Controller
#from plugins.network.models import Network, IPAddress
from resources.models import  Switch, SwitchPort, Server, VirtualSwitch, SliceSwitch
from plugins.openflow.models import Flowvisor, Controller, Link, FlowvisorLinksMd5

admin.site.register(City)
admin.site.register(Island)
admin.site.register(Project)
admin.site.register(Category)
admin.site.register(Slice)
admin.site.register(Switch)
admin.site.register(VirtualSwitch)
admin.site.register(Server)
admin.site.register(Controller)
admin.site.register(Flowvisor)
admin.site.register(SwitchPort)
admin.site.register(Membership)

admin.site.register(SliceSwitch)
admin.site.register(Link)
admin.site.register(FlowvisorLinksMd5)
