from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...search_indexes import OrganisationIndex


class Command(BaseCommand):
    help = "Index fines"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        idx = OrganisationIndex()
        idx.create()
        idx.index()
