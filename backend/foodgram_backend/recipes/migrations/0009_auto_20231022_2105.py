# Generated by Django 3.2.3 on 2023-10-22 18:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0008_alter_recipe_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="image",
            field=models.ImageField(default=None, null=True, upload_to="media/"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="color",
            field=models.CharField(
                default="#ffffff", max_length=31, null=True, unique=True
            ),
        ),
    ]
