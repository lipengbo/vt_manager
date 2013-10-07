from django.contrib import admin

from invite.models import Invitation, Application

admin.site.register(Invitation)
admin.site.register(Application)
