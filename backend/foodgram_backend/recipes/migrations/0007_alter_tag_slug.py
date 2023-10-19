# Generated by Django 3.2.3 on 2023-10-17 20:11

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_shoppingcart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, validators=[core.validators.validate_slug], verbose_name='Уникальный слаг тега'),
        ),
    ]