from django.core.management.base import BaseCommand

from ...models import Fine


class Command(BaseCommand):
    help = "Print all source files"

    def handle(self, *args, **options):
        qs = Fine.objects.all().values_list('source_file', flat=True)
        for filename in set(qs.iterator()):
            self.stdout.write((u'%s\n' % filename).encode('utf-8'))
