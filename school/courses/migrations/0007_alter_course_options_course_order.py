# Generated by Django 4.0.2 on 2023-05-30 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_remove_lessonitem_unique_lesson_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['order'], 'verbose_name': 'kurz', 'verbose_name_plural': 'kurzy'},
        ),
        migrations.AddField(
            model_name='course',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]