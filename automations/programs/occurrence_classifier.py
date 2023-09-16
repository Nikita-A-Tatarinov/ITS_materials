from django.core.exceptions import ObjectDoesNotExist
from bs4 import BeautifulSoup

from automations.models import Occurrence, ClassifiedOccurrence

import re
import spacy

nlp = spacy.load('venv/lib/python3.8/site-packages/en_core_web_lg/en_core_web_lg-3.5.0')


def classify_occurrences():
    for occurrence_obj in Occurrence.objects.all():
        try:
            occurrence_obj.classified_occurrence
        except ObjectDoesNotExist:
            classify_occurrence(occurrence_obj)


def classify_occurrence(occurrence_obj):
    content = occurrence_obj.parsed_material_section.content
    indices = [occurrence_obj.place_start, occurrence_obj.place_end]
    occurrence_text = occurrence_obj.parsed_material_section.content[indices[0]:indices[1]]
    paragraph_snippet = create_paragraph_snippet(content, indices)
    sentence_snippet = create_sentence_snippet(content, indices)
    if paragraph_snippet is None or sentence_snippet is None:
        ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                            occurrence_type='other',
                                            relevance=0,
                                            snippet='FAILED TO EXTRACT SNIPPETS',
                                            is_approved=False,
                                            default_for_section=False)
        return
    if (not check_definition(occurrence_obj, occurrence_text, paragraph_snippet, sentence_snippet)) and \
            (not check_distinction(occurrence_obj, paragraph_snippet)) and \
            (not check_example(occurrence_obj, occurrence_text, paragraph_snippet)):
        ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                            occurrence_type='other',
                                            relevance=0.5,
                                            snippet=paragraph_snippet,
                                            is_approved=False,
                                            default_for_section=False)


def create_paragraph_snippet(content, indices):
    soup = BeautifulSoup(content, 'html.parser')
    for tag in ['p', 'li', 'ol', 'ul', 'em']:
        paragraphs = soup.find_all(tag)
        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text()
            paragraph_indices = [content.find(paragraph_text), content.find(paragraph_text) + len(paragraph_text)]
            if indices[0] >= content.find(paragraph_text) and \
                    indices[1] <= content.find(paragraph_text) + len(paragraph_text):
                return paragraph_text


def create_sentence_snippet(content, indices):
    doc = nlp(content)
    for sentence in doc.sents:
        if indices[0] >= content.find(sentence.text) and \
                indices[1] <= content.find(sentence.text) + len(sentence.text):
            return sentence.text
    paragraph_snippet = create_paragraph_snippet(content, indices)
    for sentence in re.split(r'\.|!|\?|\.\.\.', paragraph_snippet):
        if indices[0] >= content.find(sentence) and indices[1] <= content.find(sentence) + len(sentence):
            return sentence


def check_definition(occurrence_obj, occurrence_text, paragraph_snippet, sentence_snippet):
    if (re.search(r'was (the )?' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(r'called (the )?' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r' refers to', sentence_snippet.lower()) is not None) or \
            (re.search(r'referred to as (the )?' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(r'define (the )?' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r' is defined', sentence_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'{\,}? which is', sentence_snippet.lower()) is not None):
        ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                            occurrence_type='definition',
                                            relevance=0.8,
                                            snippet=paragraph_snippet,
                                            is_approved=False,
                                            default_for_section=False)
        return True
    if (re.search(r'was .*' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(r'called .*' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'.* refers to', sentence_snippet.lower()) is not None) or \
            (re.search(r'referred to as .*' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(r'define .*' + occurrence_text.lower(), sentence_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'.* is defined', sentence_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'.* which is', sentence_snippet.lower()) is not None):
        ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                            occurrence_type='definition',
                                            relevance=0.6,
                                            snippet=paragraph_snippet,
                                            is_approved=False,
                                            default_for_section=False)
        return True
    if (re.search(r'was .*' + occurrence_text.lower(), paragraph_snippet.lower()) is not None) or \
            (re.search(r'called .*' + occurrence_text.lower(), paragraph_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'.* refers to', paragraph_snippet.lower()) is not None) or \
            (re.search(r'referred to as .*' + occurrence_text.lower(), paragraph_snippet.lower()) is not None) or \
            (re.search(r'define .*' + occurrence_text.lower(), paragraph_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'.* is defined', paragraph_snippet.lower()) is not None) or \
            (re.search(occurrence_text.lower() + r'.* which is', paragraph_snippet.lower()) is not None):
        ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                            occurrence_type='definition',
                                            relevance=0.4,
                                            snippet=paragraph_snippet,
                                            is_approved=False,
                                            default_for_section=False)
        return True
    if 'definition' in paragraph_snippet.lower() or \
            nlp(occurrence_obj.parsed_material_section.topic) \
                    .similarity(nlp(occurrence_obj.ontology_term.topic.name)) > 0.5:
        ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                            occurrence_type='definition',
                                            relevance=0.2,
                                            snippet=paragraph_snippet,
                                            is_approved=False,
                                            default_for_section=False)
        return True
    return False


def check_distinction(occurrence_obj, paragraph_snippet):
    if 'distinction' in paragraph_snippet.lower():
        additional_relevance = 0.2
    elif 'difference' in paragraph_snippet.lower():
        additional_relevance = 0.1
    else:
        additional_relevance = 0
    other_occurrences_in_pms = occurrence_obj.parsed_material_section.occurrences.all()
    for another_occurrence in other_occurrences_in_pms:
        if another_occurrence.ontology_term.term == occurrence_obj.ontology_term.term:
            continue
        another_occurrence_paragraph_snippet = create_paragraph_snippet(
            another_occurrence.parsed_material_section.content,
            [another_occurrence.place_start, another_occurrence.place_end])
        if paragraph_snippet != another_occurrence_paragraph_snippet:
            continue
        if another_occurrence.ontology_term.term in occurrence_obj.ontology_term.term or \
                occurrence_obj.ontology_term.term in another_occurrence.ontology_term.term:
            main_relevance = 0.4
        elif another_occurrence.ontology_term.dimension == occurrence_obj.ontology_term.dimension:
            main_relevance = 0.6
        else:
            main_relevance = 0
        if main_relevance != 0:
            ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                                occurrence_type='distinction',
                                                relevance=main_relevance + additional_relevance,
                                                snippet=paragraph_snippet,
                                                distinction_ontology_term=another_occurrence.ontology_term.term,
                                                is_approved=False,
                                                default_for_section=False)
            return True
    return False


def check_example(occurrence_obj, occurrence_text, paragraph_snippet):
    if len(paragraph_snippet) < 50:
        return False
    if (re.search(occurrence_text.lower() + r'.* is used', paragraph_snippet.lower()) is not None) or \
            (re.search(r'use .*' + occurrence_text.lower(), paragraph_snippet.lower()) is not None):
        additional_relevance = 0.2
    elif 'example' in paragraph_snippet.lower():
        additional_relevance = 0.1
    else:
        additional_relevance = 0
    ClassifiedOccurrence.objects.create(occurrence=occurrence_obj,
                                        occurrence_type='example',
                                        relevance=0.5 + additional_relevance,
                                        snippet=paragraph_snippet,
                                        is_approved=False,
                                        default_for_section=False)
    return True
