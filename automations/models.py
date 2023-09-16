from django.db import models
from db_materials.models import Material


class ParsedMaterial(models.Model):
    material = models.OneToOneField(Material,
                                    on_delete=models.CASCADE,
                                    primary_key=True,
                                    related_name='parsed_material')
    pdf_file = models.FileField(upload_to='pdf_files/')
    html_file = models.FileField(upload_to='html_files/')

    def __str__(self):
        return f'Material tag: {self.material.tag}'


class ParsedMaterialSection(models.Model):
    topic = models.CharField(max_length=255)
    parsed_material = models.ForeignKey(ParsedMaterial,
                                        on_delete=models.CASCADE,
                                        related_name='parsed_material_sections')
    level = models.IntegerField()
    super_topic = models.ForeignKey('self', on_delete=models.CASCADE, related_name='parsed_material_subsections',
                                    blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['topic', 'parsed_material'],
                name='unique_topic_parsed_material_combination'
            )
        ]

    def __str__(self):
        return f'Topic: {self.topic}; material tag: {self.parsed_material.material.tag}; level: {self.level}'


class Ontology(models.Model):
    tag = models.CharField(max_length=255, primary_key=True)
    file = models.FileField(upload_to='ontology_files/')

    def __str__(self):
        return f'Tag: {self.tag}'


class OntologyTopic(models.Model):
    name = models.CharField(max_length=255)
    ontology = models.ForeignKey(Ontology, on_delete=models.CASCADE, related_name='ontology_topics')
    super_topic = models.ForeignKey('self', on_delete=models.CASCADE, related_name='ontology_subtopics',
                                    blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'ontology'],
                name='unique_name_ontology_combination'
            )
        ]

    def __str__(self):
        return f'Name: {self.name}'


class OntologyTerm(models.Model):
    term = models.CharField(max_length=255)
    ontology = models.ForeignKey(Ontology, on_delete=models.CASCADE, related_name='ontology_terms')
    topic = models.ForeignKey(OntologyTopic, on_delete=models.CASCADE, related_name='ontology_terms')
    dimension = models.CharField(max_length=255)
    synonyms = models.TextField(blank=True, null=True)
    symbols = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['term', 'ontology'],
                name='unique_term_ontology_combination'
            )
        ]

    def __str__(self):
        return f'Term: {self.term}; ontology tag: {self.ontology.tag}'


class Occurrence(models.Model):
    parsed_material_section = models.ForeignKey(ParsedMaterialSection,
                                                on_delete=models.CASCADE,
                                                related_name='occurrences')
    ontology_term = models.ForeignKey(OntologyTerm, on_delete=models.CASCADE, related_name='ontology_terms')
    place_start = models.IntegerField()
    place_end = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['parsed_material_section', 'ontology_term', 'place_start', 'place_end'],
                name='unique_parsed_material_section_ontology_term_place_start_place_end_combination'
            )
        ]

    def __str__(self):
        return f'Parsed material section topic: {self.parsed_material_section.topic}; ' \
               f'ontology term: {self.ontology_term.term}; ' \
               f'place start: {self.place_start}; place end: {self.place_end}.'


class ClassifiedOccurrence(models.Model):
    occurrence = models.OneToOneField(Occurrence,
                                      on_delete=models.CASCADE,
                                      primary_key=True,
                                      related_name='classified_occurrence')
    OCCURRENCE_TYPE_CHOICES = (
        ('definition', 'definition'),
        ('example', 'example'),
        ('distinction', 'distinction'),
        ('other', 'other')
    )
    occurrence_type = models.CharField(max_length=255, choices=OCCURRENCE_TYPE_CHOICES)
    relevance = models.FloatField()
    snippet = models.TextField()
    distinction_ontology_term = models.CharField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(blank=True, null=True)
    default_for_section = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f'{self.occurrence}; occurrence type: {self.occurrence_type}; ' \
               f'distinction ontology term: {self.distinction_ontology_term}.'


class COUsage(models.Model):
    classified_occurrence = models.ForeignKey(ClassifiedOccurrence, on_delete=models.CASCADE, related_name='co_usages')
    usage_time = models.TimeField()

    def __str__(self):
        return f'Classified occurrence ID: {self.classified_occurrence.occurrence.id}; usage time: {self.usage_time}'
