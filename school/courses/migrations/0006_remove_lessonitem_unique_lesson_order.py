# Generated by Django 4.0.2 on 2022-02-01 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_lessonmaterial_material_id"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="lessonitem",
            name="unique_lesson_order",
        ),
    ]
