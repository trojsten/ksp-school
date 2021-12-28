# Generated by Django 4.0 on 2021-12-28 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("slug", models.CharField(max_length=64, unique=True)),
                ("content", models.TextField()),
            ],
            options={
                "verbose_name": "stránka",
                "verbose_name_plural": "stránky",
            },
        ),
    ]