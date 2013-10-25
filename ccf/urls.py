from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()
#import xadmin
#xadmin.autodiscover()

#from xadmin.plugins import xversion
#xversion.registe_models()

urlpatterns = patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^login/", TemplateView.as_view(template_name="login.html"), name="demo"),
    url(r"^help/", TemplateView.as_view(template_name="help.html"), name="demo"),
    url(r"^create_project/", TemplateView.as_view(template_name="create_project.html"), name="demo"),
    url(r"^detail_project/", TemplateView.as_view(template_name="detail_project.html"), name="demo"),
    url(r"^create_slice1/", TemplateView.as_view(template_name="create_slice1.html"), name="demo"),
    url(r"^create_slice2/", TemplateView.as_view(template_name="create_slice2.html"), name="demo"),
    url(r"^create_slice3/", TemplateView.as_view(template_name="create_slice3.html"), name="demo"),
    url(r"^create_slice4/", TemplateView.as_view(template_name="create_slice4.html"), name="demo"),
    url(r"^create_slice5/", TemplateView.as_view(template_name="create_slice5.html"), name="demo"),
    url(r"^detail_slice/", TemplateView.as_view(template_name="detail_slice.html"), name="demo"),
    url(r"^create_slice/", TemplateView.as_view(template_name="create_slice.html"), name="demo"),
    url(r"^project_manage/", TemplateView.as_view(template_name="project_manage.html"), name="proje_manage"),
    url(r"^list_project/", TemplateView.as_view(template_name="list_project.html"), name="demo"),
    url(r"^list_slice/", TemplateView.as_view(template_name="list_slice.html"), name="demo"),
    url(r"^list_vm/", TemplateView.as_view(template_name="list_vm.html"), name="demo"),
    url(r"^apply_project/", TemplateView.as_view(template_name="apply_project.html"), name="demo"),
    url(r"^homepage/", TemplateView.as_view(template_name="homepage.html"), name="demo"),
    url(r"^logs/", TemplateView.as_view(template_name="logs.html"), name="demo"),
    url(r"^logs_handle/", TemplateView.as_view(template_name="logs_handle.html"), name="demo"),
    url(r"^member_check/", TemplateView.as_view(template_name="member_check.html"), name="demo"),
    url(r"^invite_member/", TemplateView.as_view(template_name="invite_member.html"), name="demo"),

    url(r"^map/$", TemplateView.as_view(template_name="index.html"), name="map"),
    url(r"^forbidden/", TemplateView.as_view(template_name="forbidden.html"), name="forbidden"),


    url(r'^topology/$', 'project.views.topology', name="topology_view"),
    url(r'^(topology/.+\.html)$', direct_to_template, ),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/aggregate/json', 'project.views.swicth_aggregate'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/desc/json', 'project.views.swicth_desc'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/device/', 'project.views.device_proxy'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/topology/links/json', 'project.views.links_direct'),
    url(r'^direct/(?P<host>[\d\.]+):(?P<port>\d+)/wm/', 'project.views.switch_direct'),

    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/aggregate/json', 'project.views.swicth_aggregate'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/core/switch/(?P<dpid>[\w:]+)/desc/json', 'project.views.swicth_desc'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/device/', 'project.views.device_proxy'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/topology/links/json', 'project.views.links_proxy'),
    url(r'^(?P<host>[\d\.]+):(?P<port>\d+)/wm/', 'project.views.switch_proxy'),


    url(r"^project/", include("project.urls")),
    url(r"^slice/", include("slice.urls")),
    url(r"^plugins/vt/", include("plugins.vt.urls")),
    url(r"^invite/", include("invite.urls")),
    url(r"^admin/", include(admin.site.urls)),
    #url(r'^admin/', include(xadmin.site.urls)),
    url(r"^accounts/", include("account.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
