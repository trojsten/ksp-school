# Generated by Django 4.2.3 on 2023-07-11 20:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classrooms", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="classroom",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="classroomuser",
            options={
                "ordering": ["-is_teacher", "user__last_name", "user__first_name"]
            },
        ),
        migrations.AlterField(
            model_name="classroom",
            name="join_code",
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]