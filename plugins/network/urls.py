from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('network.views',
    url(r'^$', "index", name='network_index'),
)
