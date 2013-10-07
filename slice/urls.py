from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('slice.views',
    url(r'^$', "index", name='slice_index'),
    url(r'^list/(?P<proj_id>\d+)/$', "list", name='slice_list'),
    url(r'^create/(?P<proj_id>\d+)/$', "create", name='create_slice'),
    url(r'^create_first/(?P<proj_id>\d+)/$', "create_first", name='create_first_slice'),
    url(r'^delete/(?P<slice_id>\d+)/$', "delete", name='delete_slice'),
    url(r'^detail/(?P<slice_id>\d+)/$', "detail", name='slice_detail'),
    url(r'^start_or_stop/(?P<slice_id>\d+)/(?P<flag>\d+)/$', "start_or_stop", name='start_or_stop'),
    url(r'^topology/(?P<slice_id>\d+)/$', "topology", name='slice_topology'),
    url(r'^edit_description/(?P<slice_id>\d+)/$', "edit_description", name='edit_slice_description'),
    url(r'^edit_controller/(?P<slice_id>\d+)/$', "edit_controller", name='edit_slice_controller'),
    url(r'^check_slice_name/(?P<slice_name>\w+)/$', "check_slice_name", name='check_slice_name'),
    url(r'^create_nw/(?P<owner>\w+)/$', "create_nw", name='create_nw'),
    url(r'^delete_nw/(?P<owner>\w+)/$', "delete_nw", name='delete_nw'),
    url(r'^change_nw_owner/(?P<nw>\w+)/(?P<new_owner>\w+)/$', "change_nw_owner", name='change_nw_owner'),
    url(r'^change_nw/(?P<owner>\w+)/(?P<new_owner>\w+)/$', "change_nw", name='change_nw'),
)
