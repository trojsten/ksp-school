# Generated by Django 4.0.1 on 2022-01-17 22:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="submit",
            options={
                "ordering": ("-created_at",),
                "verbose_name": "submit",
                "verbose_name_plural": "submity",
            },
        ),
    ]
