import unicodecsv

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...models import Fine

BULK_SIZE = 1000


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
        self.stdout.write('Creating aggregates...\n')
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
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("UPDATE bussgelder_organisation SET sum_fines=(SELECT SUM(bussgelder_fine.amount) FROM bussgelder_fine WHERE bussgelder_fine.organisation_id=bussgelder_organisation.id);")
