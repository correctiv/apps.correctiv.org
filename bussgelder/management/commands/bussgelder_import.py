import decimal
import unicodecsv

from slugify import slugify

from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...models import Fine, Organisation

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
            yield self.create_from_row(row, fine=fine)

    def create_from_row(self, row, fine=None):
        if fine is None:
            fine = Fine()

        org_slug = slugify(row['name'])

        try:
            org = Organisation.objects.get(slug=org_slug)
        except Organisation.DoesNotExist:
            org = Organisation.objects.create(name=row['name'], slug=org_slug)

        fine.organisation = org
        fine.name = row['name']
        fine.original_name = row['orig_name']
        # path of the form data/badenwuerttemberg/2013/justiz/justiz_bawue_2013.csv
        parts = row['path'].split('/')
        fine.state = parts[1]
        fine.year = int(parts[2])
        fine.department = parts[3]
        fine.department_detail = parts[4].split('_')[1].title()
        fine.amount = decimal.Decimal(row['betrag'])
        if row['betrag_eingegangen']:
            fine.amount_received = decimal.Decimal(row['betrag_eingegangen'])

        fine.address = row['adresse']
        fine.file_reference = row['aktenzeichen']
        fine.filename = row['path']
        fine.note = row['anmerkungen']
        fine.source_file = row['source']
        fine.reference_id = row['id']
        fine.city = row['ort']
        fine.postcode = row['plz']

        fine.bank_details = u'\n'.join(
            row.get(k) for k in (
                'blz',
                'kto',
                'kreditinstitut',
                'bank',
            ) if row.get(k))

        fine.org_details = u'\n'.join(
            row.get(k) for k in (
                'kategorie',
                'notizen',
                'rest',
                'thema',
                'vorsitzender',
                'wirkungskreis',
                'zu_haenden'
            ) if row.get(k))

        return fine

    def create_aggregates(self):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("UPDATE bussgelder_organisation SET sum_fines=(SELECT SUM(bussgelder_fine.amount) FROM bussgelder_fine WHERE bussgelder_fine.organisation_id=bussgelder_organisation.id);")
