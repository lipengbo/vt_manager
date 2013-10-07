from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('openflow.views',
    url(r'^$', "index", name='openflow_index'),
)
