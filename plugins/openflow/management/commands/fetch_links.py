from optparse import make_option

from django.core.management.base import AppCommand, BaseCommand, CommandError
from django.conf import settings

from plugins.openflow.models import Link, Flowvisor, update_links

class Command(BaseCommand):
    help = ''

    def handle(self, **options):
        flowvisors = Flowvisor.objects.all()
        for flowvisor in flowvisors:
            update_links(None, flowvisor, False)

