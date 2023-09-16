# Generated by Django 4.0.8 on 2023-05-20 09:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('automations', '0007_alter_ontologyterm_dimension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occurrence',
            name='ontology_term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ontology_terms', to='automations.ontologyterm'),
        ),
    ]
