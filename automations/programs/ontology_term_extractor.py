from django.db import IntegrityError
from owlready2 import *

from automations.models import Ontology, OntologyTopic, OntologyTerm


def extract_ontology_terms(ontology_tag, ontology_topic_name):
    if ontology_tag == 'all':
        for ontology_topic_obj in OntologyTopic.objects.all():
            extract_om_terms(ontology_topic_obj.name)
    elif ontology_tag == 'om':
        extract_om_terms(ontology_topic_name)
        return True
    else:
        return False


def extract_om_terms(ontology_topic_name):
    ontology_obj = Ontology.objects.get(tag='om')
    if ontology_topic_name == 'all':
        for ontology_topic_obj in OntologyTopic.objects.filter(ontology=ontology_obj):
            extract_om_topic_terms(ontology_obj, ontology_topic_obj.name)
    else:
        extract_om_topic_terms(ontology_obj, ontology_topic_name)


def extract_om_topic_terms(ontology_obj, ontology_topic_name):
    ontology_topic_obj = OntologyTopic.objects.get(name=ontology_topic_name, ontology=ontology_obj)
    onto = get_ontology(f'file://{ontology_obj.file.path}').load()
    topics_list = onto.ApplicationArea.instances()
    for topic_class in topics_list:
        if topic_class.label[0] == ontology_topic_name:
            for term_class in topic_class.usesUnit:
                try:
                    create_ontology_term_obj(term_class.label[0], ontology_obj, ontology_topic_obj,
                                             term_class.hasDimension[0].label[0],
                                             create_synonym_str(term_class), create_symbol_str(term_class))
                except IndexError:
                    pass
            for term_class in topic_class.usesQuantity:
                try:
                    create_ontology_term_obj(term_class.label[0], ontology_obj, ontology_topic_obj,
                                             retrieve_quantity_dimension(onto, term_class),
                                             create_synonym_str(term_class), create_symbol_str(term_class))
                except IndexError:
                    pass
            break


def retrieve_quantity_dimension(onto, term_class):
    while term_class.is_a[0] != onto.Quantity:
        term_class = term_class.is_a[0]
    return term_class.hasDimension[0].label[0]


def create_ontology_term_obj(term, ontology_obj, topic, dimension, synonyms, symbols):
    try:
        OntologyTerm.objects.create(term=term,
                                    ontology=ontology_obj,
                                    topic=topic,
                                    dimension=dimension,
                                    synonyms=synonyms,
                                    symbols=symbols)
    except IntegrityError:
        pass
    except IndexError:
        pass


def create_synonym_str(term_class):
    synonym_str = ''
    for i in range(1, len(term_class.label)):
        synonym_str += (term_class.label[i] + ';')
    for alternative_label in term_class.alternativeLabel:
        synonym_str += (alternative_label + ';')
    return synonym_str[:-1]


def create_symbol_str(term_class):
    symbol_str = ''
    for symbol in term_class.symbol:
        symbol_str += (symbol + ';')
    for alternative_symbol in term_class.alternativeSymbol:
        symbol_str += (alternative_symbol + ';')
    return symbol_str[:-1]
