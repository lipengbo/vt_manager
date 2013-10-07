from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('resources.views',
    url(r'^$', "index", name='resources_index'),
)
