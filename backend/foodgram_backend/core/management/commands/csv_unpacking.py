import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(
            f'{settings.BASE_DIR}/data/ingredients.csv',
            'r',
            encoding='utf-8',
        ) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                _, created = Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
            self.stdout.write(
                self.style.SUCCESS(
                    'Данные загружены в модель'
                )
            )
