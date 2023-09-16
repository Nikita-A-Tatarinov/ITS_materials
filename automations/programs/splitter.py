from django.db import IntegrityError
from automations.models import ParsedMaterial, ParsedMaterialSection

import re


def split_into_sections(material_tag, option):
    if material_tag == 'all':
        for parsed_material_obj in ParsedMaterial.objects.all():
            if option == 'by headers':
                split_by_headers(parsed_material_obj.material.tag)
    else:
        if option == 'by headers':
            split_by_headers(material_tag)


def split_by_headers(material_tag):
    parsed_material_obj = ParsedMaterial.objects.get(material__tag=material_tag)
    with open(parsed_material_obj.html_file.path, 'r') as f:
        text = f.read()
    try:
        topics = extract_topics(text)
    except ValueError:
        pass
    except KeyError:
        pass
    for topic_num, topic_name in topics.items():
        try:
            ParsedMaterialSection.objects.create(topic=topic_name, parsed_material=parsed_material_obj, level=0)
        except IntegrityError:
            pass
    try:
        subtopics = extract_subtopics(text)
    except ValueError:
        pass
    except KeyError:
        pass
    for topic_num, topic_dict in subtopics.items():
        for subtopic_name, subtopic_name in topic_dict.items():
            try:
                super_topic_obj = ParsedMaterialSection.objects.get(topic=topics[topic_num],
                                                                    parsed_material=parsed_material_obj)
                try:
                    ParsedMaterialSection.objects.create(topic=subtopic_name,
                                                         parsed_material=parsed_material_obj,
                                                         super_topic=super_topic_obj,
                                                         level=1)
                except IntegrityError:
                    pass
            except ValueError:
                pass
            except KeyError:
                pass
    fill_contents(text, topics, subtopics)


def extract_topics(text):
    pattern = r'^<p>\d+ [A-Z]{2,}\,?\;?\:?(?:\’S)?(?: [A-Z]+\,?\;?\:?(?:\’S)?)*<\/p>$'
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    matches = [match[3:-4] for match in matches]
    topics = {}
    for match in matches:
        num = int(re.findall(r'\d+', match)[0])
        topics[num] = re.sub(r'\d+', '', match)[1:].lower()
    return topics


def extract_subtopics(text):
    pattern = r'^<p>\d+–\d+ \(?“?\’?[A-Za-z]+\’?”?\)?\.?\??\,?\;?\:?(?:[—–\-][A-Za-z]+)?(?:\’[Ss])?' \
              r'(?: \(?“?\’?[A-Za-z]+\’?”?\)?\.?\??\,?\;?\:?(?:[—–\-][A-Za-z]+)?(?:\’[Ss])?)*\s*<\/p>$'
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    matches = [match[3:-4] for match in matches]
    subtopics = {}
    for match in matches:
        nums_str = re.findall(r'\d+', match)
        topic_num = int(nums_str[0])
        subtopic_num = int(nums_str[1])
        if topic_num not in subtopics:
            subtopics[topic_num] = {}
        subtopics[topic_num][subtopic_num] = re.sub(r'\d+–\d+ ', '', match).lower()
    return subtopics


def fill_contents(text, topics, subtopics):
    topic_pattern = r'^<p>\d+ [A-Z]{2,}\,?\;?\:?(?:\’S)?(?: [A-Z]+\,?\;?\:?(?:\’S)?)*<\/p>$'
    subtopic_pattern = r'^<p>\d+–\d+ \(?“?\’?[A-Za-z]+\’?”?\)?\.?\??\,?\;?\:?(?:[—–\-][A-Za-z]+)?(?:\’[Ss])?' \
                       r'(?: \(?“?\’?[A-Za-z]+\’?”?\)?\.?\??\,?\;?\:?(?:[—–\-][A-Za-z]+)?(?:\’[Ss])?)*\s*<\/p>$'
    sections = re.split(topic_pattern, text, flags=re.MULTILINE)
    for i in range(1, len(sections)):
        subsections = re.split(subtopic_pattern, sections[i], flags=re.MULTILINE)
        for j in range(1, len(subsections)):
            subtopic_obj = ParsedMaterialSection.objects.get(
                topic=list(list(subtopics.values())[i - 1].values())[j - 1])
            subtopic_obj.content = subsections[j]
            subtopic_obj.save()
