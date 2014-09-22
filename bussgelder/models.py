# -*- encoding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse


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
    ('sachsen-anhalt', u'Sachsen-Anhalt'),
    ('schleswig-holstein', u'Schleswig-Holstein'),
    ('thueringen', u'Thüringen')
)
GERMAN_STATES_DICT = dict(GERMAN_STATES)


class Organisation(models.Model):
    name = models.CharField(max_length=512)
    slug = models.SlugField(max_length=255)
    sum_fines = models.DecimalField(null=True, decimal_places=2, max_digits=19)
    note = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bussgelder:organisation_detail', kwargs={'slug': self.slug})


class FineManager(models.Manager):
    def all_with_amount(self):
        return self.get_queryset().exclude(amount=0.0)


class Fine(models.Model):

    DEPARTMENTS = (
        ('sta', u'Staatsanwaltschaft'),
        ('justiz', u'Justizministerium'),
        ('lg', u'Landgericht'),
        ('ag', u'Amtsgericht'),
        ('olg', u'Oberlandesgericht'),
    )
    DEPARTMENTS_DICT = dict(DEPARTMENTS)

    organisation = models.ForeignKey(Organisation, related_name='fines')
    name = models.CharField(max_length=512)
    original_name = models.CharField(max_length=512)

    year = models.SmallIntegerField()

    state = models.CharField(max_length=25, choices=GERMAN_STATES)
    department = models.CharField(max_length=10, choices=DEPARTMENTS)
    department_detail = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(decimal_places=2, max_digits=19)
    amount_received = models.DecimalField(null=True, decimal_places=2,
                                          max_digits=19, blank=True)

    address = models.TextField(blank=True)
    file_reference = models.CharField(max_length=255, blank=True)
    source_file = models.CharField(max_length=255, blank=True)
    bank_details = models.TextField(blank=True)
    org_details = models.TextField(blank=True)
    filename = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=255)

    note = models.TextField(blank=True)

    city = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=5, blank=True)

    objects = FineManager()

    class Meta:
        ordering = ('-year', 'state', '-amount')

    def __unicode__(self):
        return self.reference_id

    @property
    def state_label(self):
        return GERMAN_STATES_DICT[self.state]

    @property
    def department_label(self):
        return self.DEPARTMENTS_DICT[self.department] + ' ' + self.department_detail

    @property
    def source_file_extension(self):
        if self.source_file and '.' in self.source_file:
            return self.source_file.rsplit('.', 1)[1]
        return '???'

    @property
    def source_file_url(self):
        if self.source_file:
            if not self.source_file.rsplit('.', 1)[0].endswith('_'):
                # File is not 'secret'
                return 'justizgelder/' + self.source_file
        return ''
