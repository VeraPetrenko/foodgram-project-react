# Generated by Django 3.2.3 on 2023-09-28 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_tag_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='recipes/media/'),
        ),
    ]