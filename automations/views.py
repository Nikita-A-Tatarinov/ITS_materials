from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render
from rest_framework import generics, permissions

from automations.forms import ConverterForm, SplitterForm, OntologyTopicExtractorForm, OntologyTermExtractorForm, \
    OccurrenceExtractorForm
from automations.models import ClassifiedOccurrence, COUsage
from automations.programs.converter import convert
from automations.programs.occurrence_classifier import classify_occurrences
from automations.programs.occurrence_extractor import extract_occurrences
from automations.programs.ontology_term_extractor import extract_ontology_terms
from automations.programs.ontology_topic_extractor import extract_ontology_topics
from automations.programs.splitter import split_into_sections
from automations.serializers import COUsageSerializer


@login_required(login_url='admin:index')
def converter_view(request):
    if request.method == 'POST':
        form = ConverterForm(request.POST)
        submit_action = request.POST.get('submit_action')
        if submit_action == 'back_to_admin':
            return redirect('admin:index')
        if form.is_valid():
            data = form.cleaned_data
            if data['material_tag'] == 'none':
                messages.error(request, 'No material to parse!')
            else:
                try:
                    convert(data['material_tag'])
                    if data['split_into_sections']:
                        split_into_sections(data['material_tag'], data['split_option'])
                        messages.success(request, 'Successfully converted and split!')
                    else:
                        messages.success(request, 'Successfully converted!')
                except Exception as e:
                    messages.error(request, str(e))
    else:
        form = ConverterForm()
    return render(request, 'converter.html', {'form': form})


@login_required(login_url='admin:index')
def splitter_view(request):
    if request.method == 'POST':
        form = SplitterForm(request.POST)
        submit_action = request.POST.get('submit_action')
        if submit_action == 'back_to_admin':
            return redirect('admin:index')
        if form.is_valid():
            try:
                data = form.cleaned_data
                if data['parsed_material_tag'] == 'none':
                    messages.error(request, 'No parsed material to split!')
                else:
                    split_into_sections(data['parsed_material_tag'], data['split_option'])
                    messages.success(request, 'Successfully split!')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = SplitterForm()
    return render(request, 'splitter.html', {'form': form})


@login_required(login_url='admin:index')
def ontology_topic_extractor_view(request):
    if request.method == 'POST':
        form = OntologyTopicExtractorForm(request.POST)
        submit_action = request.POST.get('submit_action')
        if submit_action == 'back_to_admin':
            return redirect('admin:index')
        if form.is_valid():
            try:
                data = form.cleaned_data
                if data['ontology_tag'] == 'none':
                    messages.error(request, 'No ontology to extract topics from!')
                else:
                    if extract_ontology_topics(data['ontology_tag']):
                        messages.success(request, 'Successfully extracted ontology topics!')
                    else:
                        messages.error(request, 'Extractor for this ontology is not implemented yet!')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = OntologyTopicExtractorForm()
    return render(request, 'ontology_topic_extractor.html', {'form': form})


@login_required(login_url='admin:index')
def ontology_term_extractor_view(request):
    if request.method == 'POST':
        form = OntologyTermExtractorForm(request.POST)
        submit_action = request.POST.get('submit_action')
        if submit_action == 'back_to_admin':
            return redirect('admin:index')
        try:
            form.update_choices()
            if submit_action == 'extract_terms':
                if form.is_valid():
                    data = form.cleaned_data
                    if data['ontology_tag'] == 'none':
                        messages.error(request, 'No ontology to extract terms from!')
                    else:
                        if data['ontology_tag'] != 'all' and data['ontology_topic_name'] is None:
                            messages.error(request, 'No ontology topic chosen!')
                        elif extract_ontology_terms(data['ontology_tag'],
                                                    data['ontology_topic_name'].name
                                                    if (data['ontology_tag'] != 'all')
                                                    else 'all'):
                            messages.success(request, 'Successfully extracted ontology terms!')
                        else:
                            messages.error(request, 'Extractor for this ontology is not implemented yet!')
        except Exception as e:
            messages.error(request, str(e))
    else:
        form = OntologyTermExtractorForm()
    return render(request, 'ontology_term_extractor.html', {'form': form})


@login_required(login_url='admin:index')
def occurrence_extractor_view(request):
    if request.method == 'POST':
        form = OccurrenceExtractorForm(request.POST)
        submit_action = request.POST.get('submit_action')
        if submit_action == 'back_to_admin':
            return redirect('admin:index')
        try:
            if form.is_valid():
                data = form.cleaned_data
                if data['parsed_material_tag'] == 'none':
                    messages.error(request, 'No parsed material to find occurrences in!')
                elif data['ontology_term'] is None:
                    messages.error(request, 'No chosen ontology term!')
                else:
                    extract_occurrences(data['parsed_material_tag'], data['ontology_term'])
                    messages.success(request, 'Successfully extracted occurrences!')
        except Exception as e:
            messages.error(request, str(e))
    else:
        form = OccurrenceExtractorForm()
    return render(request, 'occurrence_extractor.html', {'form': form})


@login_required(login_url='admin:index')
def occurrence_classifier_view(request):
    if request.method == 'POST':
        submit_action = request.POST.get('submit_action')
        if submit_action == 'back_to_admin':
            return redirect('admin:index')
        try:
            classify_occurrences()
            messages.success(request, 'Successfully classified occurrences!')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'occurrence_classifier.html')


class COUsageAPIView(generics.ListAPIView):
    queryset = COUsage.objects.all()
    serializer_class = COUsageSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


@login_required(login_url='admin:index')
def classified_occurrence_view(request):
    if request.method == 'POST':
        try:
            queryset = ClassifiedOccurrence.objects.order_by('occurrence__id')
            page_number = int(request.POST.get('cur_page_num'))
            for i in range(20 * (page_number - 1), 20 * page_number):
                co_obj = queryset[i:i + 1].get()
                for edit_type in ['is_approved', 'default_for_section']:
                    with transaction.atomic():
                        setattr(co_obj, edit_type, False)
                        co_obj.save()
            for checkbox_type in ['is_approved', 'default_for_section']:
                value_list = request.POST.getlist(checkbox_type)
                for field_value in value_list:
                    co_obj = ClassifiedOccurrence.objects.get(occurrence__id=int(field_value))
                    setattr(co_obj, checkbox_type, True)
                    co_obj.save()
        except Exception as e:
            pass
        return redirect('automations:classified_occurrence_view')
    queryset = ClassifiedOccurrence.objects.all().order_by('occurrence__id')
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'classified_occurrence_view.html', context)
