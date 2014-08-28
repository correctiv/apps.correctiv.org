import unicodecsv

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings
from django.db.models import Sum

from ...models import Fine, Organisation

BULK_SIZE = 500


class Command(BaseCommand):
    help = "Import CSV"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        filename = args[0]

        collection = []
        for fine in self.get_fine_objects(filename):
            collection.append(fine)
            if len(collection) > BULK_SIZE:
                Fine.objects.bulk_create(collection)
                collection = []

        Fine.objects.bulk_create(collection)
        self.create_aggregates()

    def get_fine_objects(self, filename):
        for row in unicodecsv.DictReader(file(filename)):
            fine = None
            try:
                fine = Fine.objects.get(
                    file_reference=row['id']
                )
            except Fine.DoesNotExist:
                pass
            yield Fine.objects.create_from_row(row, fine=fine)

    def create_aggregates(self):
        for org in Organisation.objects.annotate(sum_of_fines=Sum('fines__amount')).iterator():
            org.sum_fines = org.sum_of_fines
            org.save()
