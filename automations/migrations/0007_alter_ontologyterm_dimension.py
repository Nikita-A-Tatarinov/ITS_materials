# Generated by Django 4.0.8 on 2023-05-20 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automations', '0006_ontologyterm_dimension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ontologyterm',
            name='dimension',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
