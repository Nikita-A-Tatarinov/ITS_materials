from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db import IntegrityError
from spacy.matcher import Matcher

from automations.models import ParsedMaterial, ParsedMaterialSection, Occurrence

import spacy

nlp = spacy.load('venv/lib/python3.8/site-packages/en_core_web_sm/en_core_web_sm-3.5.0')


def extract_occurrences(parsed_material_tag, ontology_term_obj):
    if parsed_material_tag == 'all':
        for parsed_material_obj in ParsedMaterial.objects.all():
            extract_pm_occurrences(parsed_material_obj.material.tag, ontology_term_obj)
    else:
        extract_pm_occurrences(parsed_material_tag, ontology_term_obj)
    pass


def extract_pm_occurrences(parsed_material_tag, ontology_term_obj):
    query = create_query(ontology_term_obj)
    relevant_sections = ParsedMaterialSection.objects.annotate(
        search=SearchVector('content', config='english')
    ).filter(search=query).filter(parsed_material__material__tag=parsed_material_tag)
    matcher = Matcher(nlp.vocab)
    matcher.add('TermAndSynonyms', create_patterns(ontology_term_obj))
    for parsed_material_section_obj in relevant_sections:
        if parsed_material_section_obj.content is None:
            continue
        pms_text = nlp(parsed_material_section_obj.content)
        matches = matcher(pms_text)
        for match_id, start, end in matches:
            matched_tokens = pms_text[start:end]
            try:
                Occurrence.objects.create(parsed_material_section=parsed_material_section_obj,
                                          ontology_term=ontology_term_obj,
                                          place_start=matched_tokens.start_char,
                                          place_end=matched_tokens.end_char - 1)
            except IntegrityError:
                pass


def create_query(ontology_term_obj):
    query = SearchQuery(ontology_term_obj.term, search_type='phrase', config='english')
    for synonym in ontology_term_obj.synonyms.split(';'):
        query = (query | SearchQuery(synonym, search_type='phrase', config='english'))
    return query


def create_patterns(ontology_term_obj):
    patterns = []
    patterns.append(create_pattern(ontology_term_obj.term))
    for synonym in ontology_term_obj.synonyms.split(';'):
        patterns.append(create_pattern(synonym))
    return patterns


def create_pattern(term):
    pattern = []
    for term_word in term.split():
        pattern.append({'LOWER': term_word})
    return pattern
