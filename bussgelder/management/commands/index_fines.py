from django.core.management.base import BaseCommand
from django.utils import translation
from django.conf import settings

from ...search_indexes import FineIndex


class Command(BaseCommand):
    help = "Index fines"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        idx = FineIndex()
        idx.create()
        idx.index()
