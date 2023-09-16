from django.urls import path

from automations.views import converter_view, splitter_view, ontology_topic_extractor_view, \
    ontology_term_extractor_view, occurrence_extractor_view, occurrence_classifier_view, \
    COUsageAPIView, classified_occurrence_view

app_name = 'automations'

urlpatterns = [
    path("converter/", converter_view, name="converter"),
    path("splitter/", splitter_view, name="splitter"),
    path("ontology_topic_extractor/", ontology_topic_extractor_view, name="ontology_topic_extractor"),
    path("ontology_term_extractor/", ontology_term_extractor_view, name="ontology_term_extractor"),
    path("occurrence_extractor/", occurrence_extractor_view, name="occurrence_extractor"),
    path("occurrence_classifier/", occurrence_classifier_view, name="occurrence_classifier"),
    path("co_usages/", COUsageAPIView.as_view(), name="co_usages"),
    path("classified_occurrence_view/", classified_occurrence_view, name="classified_occurrence_view"),
]
