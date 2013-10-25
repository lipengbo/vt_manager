import xadmin
from xadmin import views
from models import *
from xadmin.layout import *

from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction

from resources.models import Switch, Server, VirtualSwitch


class ServerAdmin(object):
    list_display = ('name', 'island', 'ip', 'state')
    list_display_links = ('name',)

    search_fields = ['name']
    style_fields = {'hosts': 'checkbox-inline'}

xadmin.site.register(Server, ServerAdmin)
xadmin.site.register(Switch)
xadmin.site.register(VirtualSwitch)
