from django.db import models


class Material(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    edition = models.IntegerField(blank=True, null=True)
    url = models.URLField()
    tag = models.CharField(max_length=255, unique=True)
    create_on = models.DateField()
    update_on = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'Tag: {self.tag}; title: {self.title}; authors: {self.authors}'


class MaterialElement(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='material_elements')
    MATERIAL_ELEMENT_TYPE_CHOICES = (
        ('definition', 'definition'),
        ('example', 'example'),
        ('distinction', 'distinction'),
        ('other', 'other')
    )
    material_element_type = models.CharField(max_length=255, choices=MATERIAL_ELEMENT_TYPE_CHOICES)
    content = models.TextField()
    ontology_term = models.CharField(max_length=255)
    distinction_ontology_term = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Material tag: {self.material.tag}; material element type name: {self.material_element_type}; ' \
               f'ontology term: {self.ontology_term}; distinction ontology term: {self.distinction_ontology_term}.'


class MEUsage(models.Model):
    material_element = models.ForeignKey(MaterialElement, on_delete=models.CASCADE, related_name='me_usages')
    usage_time = models.TimeField()

    def __str__(self):
        return f'Material element ID: {self.material_element}; usage time: {self.usage_time}.'
