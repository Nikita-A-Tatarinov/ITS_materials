from django.contrib import admin

from automations.models import ParsedMaterial, ParsedMaterialSection, Ontology, OntologyTopic, OntologyTerm, \
    Occurrence, ClassifiedOccurrence

admin.site.register(ParsedMaterial)
admin.site.register(ParsedMaterialSection)
admin.site.register(Ontology)
admin.site.register(OntologyTopic)
admin.site.register(OntologyTerm)
admin.site.register(Occurrence)
admin.site.register(ClassifiedOccurrence)
