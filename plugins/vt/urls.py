from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('plugins.vt.views',
    url(r'^create/vm/(?P<sliceid>\d+)/$', "create_vm", name='create_vm'),
    url(r'^vm/list/(?P<sliceid>\d+)/$', "vm_list", name='vm_list'),
    url(r'^get_vms_state/(?P<sliceid>\d+)/$', "get_vms_state_by_sliceid", name='get_vms_state'),
    url(r'^delete/vm/(?P<vmid>\d+)/(?P<flag>\d+)/$', "delete_vm", name='delete_vm'),
    url(r'^vm/vnc/(?P<vmid>\d+)/$', "vnc", name='vm_vnc'),
    url(r'^do/vm/action/(?P<vmid>\d+)/(?P<action>\w+)/$', "do_vm_action", name='do_vm_action')
)
