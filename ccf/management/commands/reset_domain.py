from optparse import make_option

from django.core.management.base import AppCommand, BaseCommand, CommandError
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = ''

    def handle(self, **options):
        site = Site.objects.get_current()
        site.domain = settings.SITE_DOMAIN
        site.save()
