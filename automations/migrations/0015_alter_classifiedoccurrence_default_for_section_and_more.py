# Generated by Django 4.0.8 on 2023-05-30 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automations', '0014_delete_classifiedoccurrenceviewmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classifiedoccurrence',
            name='default_for_section',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='classifiedoccurrence',
            name='is_approved',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
