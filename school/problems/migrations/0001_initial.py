# Generated by Django 4.0 on 2021-12-29 13:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Problem",
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
                ("name", models.CharField(max_length=64, verbose_name="názov")),
                ("content", models.TextField(blank=True, verbose_name="zadanie")),
                (
                    "testovac_id",
                    models.CharField(
                        max_length=128, verbose_name="ID úlohy pre testovač"
                    ),
                ),
            ],
            options={
                "verbose_name": "úloha",
                "verbose_name_plural": "úlohy",
            },
        ),
        migrations.CreateModel(
            name="Submit",
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
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="čas"
                    ),
                ),
                (
                    "code",
                    models.TextField(blank=True, verbose_name="odovzdaný program"),
                ),
                ("language", models.CharField(max_length=16, verbose_name="jazyk")),
                ("protocol", models.TextField(blank=True, verbose_name="protokol")),
                (
                    "result",
                    models.CharField(blank=True, max_length=16, verbose_name="verdikt"),
                ),
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="problems.problem",
                        verbose_name="úloha",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.user",
                        verbose_name="používateľ",
                    ),
                ),
            ],
            options={
                "verbose_name": "submit",
                "verbose_name_plural": "submity",
            },
        ),
    ]
