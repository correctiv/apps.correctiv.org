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

        fields = {
            'name': 'name',
            'original_name': 'orig_name',
            'amount': 'betrag',
            'filename': 'path',
            'note': 'anmerkungen',
            'amount_received': 'betrag_eingegangen',
            'address': 'adresse',
            'file_reference': 'aktenzeichen',
            'source_file': 'source',
            'reference_id': 'id',
            'city': 'ort',
            'postcode': 'plz'
        }

        writer = unicodecsv.DictWriter(sys.stdout, fields.values())
        writer.writeheader()
        qs = Fine.objects.iterator()
        for fine in qs:
            writer.writerow(dict([(v, unicode(getattr(fine, k))) for k, v in
                            fields.items() if getattr(fine, k, None) is not None]))
