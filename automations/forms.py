from django import forms

from automations.models import ParsedMaterial, Ontology, OntologyTopic, OntologyTerm
from db_materials.models import Material


class ConverterForm(forms.Form):
    material_tag = forms.ChoiceField(label='Material tag:')
    split_into_sections = forms.BooleanField(label='Split into sections:', required=False)
    SPLIT_OPTION_CHOICES = (
        ('by headers', 'by headers'),
    )
    split_option = forms.ChoiceField(label='Split options:', choices=SPLIT_OPTION_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(m.tag, m.tag) for m in Material.objects.all()]
        if len(choices) == 0:
            self.fields['material_tag'].choices = [('none', 'none')]
        else:
            self.fields['material_tag'].choices = [('all', 'all')] + choices


class SplitterForm(forms.Form):
    parsed_material_tag = forms.ChoiceField(label='Parsed material tag:')
    split_option = forms.ChoiceField(label='Split options:', choices=ConverterForm.SPLIT_OPTION_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(pm.material.tag, pm.material.tag) for pm in ParsedMaterial.objects.all()]
        if len(choices) == 0:
            self.fields['parsed_material_tag'].choices = [('none', 'none')]
        else:
            self.fields['parsed_material_tag'].choices = [('all', 'all')] + choices


class OntologyTopicExtractorForm(forms.Form):
    ontology_tag = forms.ChoiceField(label='Ontology tag:')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(ont.tag, ont.tag) for ont in Ontology.objects.all()]
        if len(choices) == 0:
            self.fields['ontology_tag'].choices = [('none', 'none')]
        else:
            self.fields['ontology_tag'].choices = [('all', 'all')] + choices


class OntologyTermExtractorForm(forms.Form):
    ontology_tag = forms.ChoiceField(label='Ontology tag:')
    ontology_topic_name = forms.ModelChoiceField(label='Ontology topic name',
                                                 queryset=OntologyTopic.objects.none(),
                                                 required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(ont.tag, ont.tag) for ont in Ontology.objects.all()]
        if len(choices) == 0:
            self.fields['ontology_tag'].choices = [('none', 'none')]
        else:
            self.fields['ontology_tag'].choices = [('all', 'all')] + choices
        self.fields['ontology_topic_name'].queryset = OntologyTopic.objects.none()

    def update_choices(self):
        ontology_tag_value = self.data.get('ontology_tag')
        if ontology_tag_value != 'none':
            if ontology_tag_value == 'all':
                self.fields['ontology_topic_name'].queryset = OntologyTopic.objects.none()
            else:
                self.fields['ontology_topic_name'].queryset = OntologyTopic.objects.filter(
                    ontology__tag=ontology_tag_value)


class OccurrenceExtractorForm(forms.Form):
    parsed_material_tag = forms.ChoiceField(label='Parsed material tag:')
    ontology_term = forms.ModelChoiceField(label='Ontology term:',
                                           queryset=OntologyTerm.objects.all(),
                                           required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(pm.material.tag, pm.material.tag) for pm in ParsedMaterial.objects.all()]
        if len(choices) == 0:
            self.fields['parsed_material_tag'].choices = [('none', 'none')]
        else:
            self.fields['parsed_material_tag'].choices = [('all', 'all')] + choices
        self.fields['ontology_term'].queryset = OntologyTerm.objects.all()
