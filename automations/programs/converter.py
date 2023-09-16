from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from pdfminer.high_level import extract_text

from automations.models import ParsedMaterial
from db_materials.models import Material

import gdown
import os
import markdown
import re


def convert(material_tag):
    if material_tag == 'all':
        for material_obj in Material.objects.all():
            convert_material(material_obj.tag)
    else:
        convert_material(material_tag)


def convert_material(material_tag):
    try:
        ParsedMaterial.objects.get(material__tag=material_tag)
    except ObjectDoesNotExist:
        create_parsed_material_obj(material_tag)


def create_parsed_material_obj(material_tag):
    material_obj = Material.objects.get(tag=material_tag)
    pdf_material_name = f'{material_tag}.pdf'
    html_material_name = f'{material_tag}.html'
    gdown.download(url=str(material_obj.url), output=pdf_material_name, quiet=False, fuzzy=True)
    create_html(pdf_material_name, html_material_name)
    with open(pdf_material_name, 'rb') as f_pdf:
        with open(html_material_name, 'r') as f_html:
            delete_if_exists(pdf_material_name)
            delete_if_exists(html_material_name)
            ParsedMaterial.objects.create(material=material_obj,
                                          pdf_file=File(f_pdf, name=pdf_material_name),
                                          html_file=File(f_html, name=html_material_name))
    os.remove(pdf_material_name)
    os.remove(html_material_name)


def delete_if_exists(name):
    file_path = f'./{"pdf_files" if name.endswith(".pdf") else "html_files"}/{name}'
    if os.path.isfile(file_path):
        os.remove(file_path)


def create_html(path_to_pdf, path_to_html):
    text = extract_text(path_to_pdf)
    html_text = markdown.markdown(text)
    html_text = re.sub(' +', ' ', html_text)
    html_text = re.sub(' \n', '\n', html_text)
    html_text = re.sub('&.&?;', '', html_text)
    with open(path_to_html, 'w') as f:
        f.write(html_text)
