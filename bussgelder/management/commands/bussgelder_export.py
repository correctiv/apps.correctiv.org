import sys
import unicodecsv

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...models import Fine

BULK_SIZE = 1000


class Command(BaseCommand):
    help = "Export CSV"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        fields = ('name', 'original_name', 'amount', 'state', 'year',
                  'department', 'department_detail')
        writer = unicodecsv.DictWriter(sys.stdout, fields)
        writer.writeheader()
        qs = Fine.objects.filter(state='bayern', department_detail__startswith='Muenchen')
        for fine in qs:
            writer.writerow(dict([(k, unicode(getattr(fine, k))) for k in fields]))
