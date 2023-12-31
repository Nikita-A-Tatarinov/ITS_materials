# Generated by Django 4.0.8 on 2023-05-19 03:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('authors', models.CharField(max_length=255)),
                ('edition', models.IntegerField(blank=True, null=True)),
                ('url', models.URLField()),
                ('tag', models.CharField(max_length=255, unique=True)),
                ('create_on', models.DateField()),
                ('update_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialElement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_element_type', models.CharField(choices=[('definition', 'definition'), ('example', 'example'), ('distinction', 'distinction'), ('other', 'other')], max_length=255)),
                ('content', models.TextField()),
                ('ontology_term', models.CharField(max_length=255)),
                ('distinction_ontology_term', models.CharField(blank=True, max_length=255, null=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='material_elements', to='db_materials.material')),
            ],
        ),
        migrations.CreateModel(
            name='MEUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usage_time', models.TimeField()),
                ('material_element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='me_usages', to='db_materials.materialelement')),
            ],
        ),
    ]
