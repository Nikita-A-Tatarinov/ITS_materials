from django.db import IntegrityError
from owlready2 import *

from automations.models import Ontology, OntologyTopic


def extract_ontology_topics(ontology_tag):
    if ontology_tag == 'all' or ontology_tag == 'om':
        extract_om_topics()
        return True
    else:
        return False


def extract_om_topics():
    ontology_obj = Ontology.objects.get(tag='om')
    onto = get_ontology(f'file://{ontology_obj.file.path}').load()
    topics_list = onto.ApplicationArea.instances()
    for topic in topics_list:
        try:
            OntologyTopic.objects.create(name=topic.label[0], ontology=ontology_obj)
        except IntegrityError:
            pass
