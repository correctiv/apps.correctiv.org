# -*- encoding: utf-8 -*-
import decimal

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


GERMAN_STATES = (
    ('baden-wuerttemberg', u'Baden-Württemberg'),
    ('bayern', u'Bayern'),
    ('berlin', u'Berlin'),
    ('brandenburg', u'Brandenburg'),
    ('bremen', u'Bremen'),
    ('hamburg', u'Hamburg'),
    ('hessen', u'Hessen'),
    ('mecklenburg-vorpommern', u'Mecklenburg-Vorpommern'),
    ('niedersachsen', u'Niedersachsen'),
    ('nordrhein-westfalen', u'Nordrhein-Westfalen'),
    ('rheinland-pfalz', u'Rheinland-Pfalz'),
    ('saarland', u'Saarland'),
    ('sachsen', u'Sachsen'),
    ('sachsenanhalt', u'Sachsen-Anhalt'),
    ('schleswigholstein', u'Schleswig-Holstein'),
    ('thueringen', u'Thüringen')
)
GERMAN_STATES_DICT = dict(GERMAN_STATES)


class Organisation(models.Model):
    name = models.CharField(max_length=512)
    slug = models.SlugField()
    sum_fines = models.DecimalField(null=True, decimal_places=2, max_digits=19)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bussgelder_organisation_detail', kwargs={'slug': self.slug})


class FineManager(models.Manager):
    def create_from_row(self, row, fine=None):
        if fine is None:
            fine = Fine()

        org_slug = slugify(row['name'])

        try:
            org = Organisation.objects.get(slug=org_slug)
        except Organisation.DoesNotExist:
            org = Organisation.objects.create(name=row['name'], slug=org_slug)

        fine.organisation = org
        fine.original_name = row['orig_name']
        # E.g. data/badenwuerttemberg/2013/justiz/justiz_bawue_2013.csv
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

        # Bank details
        bank_detail_types = {
            'blz': u'BLZ',
            'kto': u'Kontonummer',
            'kreditinstitut': u'Kreditinstitut',
            'bank': u'Bankdetails'
        }
        fine.bank_details = u'\n'.join([
            u'%s: %s' % (v, row[k]) for k, v
            in bank_detail_types.items() if row[k]])

        org_detail_types = {
            'kategorie': u'Kategorie',
            'notizen': u'Notizen',
            'rest': u'Weitere Details',
            'thema': u'Thema',
            'vorsitzender': u'Vorsitzende(r)',
            'wirkungskreis': u'Wirkungskreis',
            'zu_haenden': u'zu Händen'
        }

        fine.org_details = u'\n'.join([
            u'%s: %s' % (v, row[k]) for k, v
            in org_detail_types.items() if row[k]])

        fine.filename = row['path']
        fine.reference_id = row['id']

        fine.city = row['ort']
        fine.postcode = row['plz']

        return fine


class Fine(models.Model):

    DEPARTMENTS = (
        ('sta', u'Staatsanwaltschaft'),
        ('justiz', u'Justizministerium'),
        ('lg', u'Landgericht'),
        ('olg', u'Oberlandgericht'),
    )

    organisation = models.ForeignKey(Organisation, related_name='fines')
    original_name = models.CharField(max_length=512)

    year = models.SmallIntegerField()

    state = models.CharField(max_length=25, choices=GERMAN_STATES)
    department = models.CharField(max_length=10, choices=DEPARTMENTS)
    department_detail = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(decimal_places=2, max_digits=19)
    amount_received = models.DecimalField(null=True, decimal_places=2, max_digits=19)

    address = models.TextField(blank=True)
    file_reference = models.CharField(max_length=255, blank=True)
    bank_details = models.TextField(blank=True)
    org_details = models.TextField(blank=True)
    filename = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=255, db_index=True)

    city = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=5, blank=True)

    objects = FineManager()

    def __unicode__(self):
        return self.reference_id

    @property
    def state_label(self):
        return GERMAN_STATES_DICT[self.state]
