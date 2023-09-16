from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from automations.models import ClassifiedOccurrence, COUsage
from db_materials.models import MaterialElement, MEUsage
from db_materials.serializers import MEUsageSerializer, ScaffoldingRequestSerializer


class MEUsageAPIView(generics.ListAPIView):
    queryset = MEUsage.objects.all()
    serializer_class = MEUsageSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class ScaffoldingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='ontology_term',
                             description='A term to return links for',
                             type=str,
                             examples=[
                                 OpenApiExample('\'metre\''),
                                 OpenApiExample('\'second\'')
                             ]),
            OpenApiParameter(name='distinction_ontology_term',
                             required=False,
                             description='An optional term to return distinction links with the required term for',
                             type=str,
                             examples=[
                                 OpenApiExample('\'centimetre\''),
                                 OpenApiExample('\'millisecond\'')
                             ]),
            OpenApiParameter(name='link_type',
                             required=False,
                             description='Required type of link between ontology and material element. '
                                         'Must by one of ["any", "definition", "example", "distinction", "other"]. '
                                         'Default is "any"',
                             type=str),
            OpenApiParameter(name='number_of_responses',
                             required=False,
                             description='Number of material elements to return. '
                                         'Must be non-negative. If 0, all the links are returned. Default is 1',
                             type=int),
        ],
        request=ScaffoldingRequestSerializer
    )
    def post(self, request, format=None):
        serializer = ScaffoldingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        if 'link_type' in data and data['link_type'] == 'distinction':
            if 'distinction_ontology_term' not in data:
                return Response('Error: distinction_ontology_term is required when link_type is distinction',
                                status=status.HTTP_400_BAD_REQUEST)
            relevant_material_elements = \
                MaterialElement.objects.filter(
                    ontology_term=data['ontology_term']).filter(
                    distinction_ontology_term=data['distinction_ontology_term'])
            relevant_classified_occurrences = ClassifiedOccurrence.objects.filter(
                occurrence__ontology_term__term=data['ontology_term']).filter(
                distinction_ontology_term=data['distinction_ontology_term']).filter(
                is_approved=True).order_by('relevance')
        else:
            relevant_material_elements = MaterialElement.objects.filter(
                ontology_term=data['ontology_term'])
            relevant_classified_occurrences = ClassifiedOccurrence.objects.filter(
                occurrence__ontology_term__term=data['ontology_term']).filter(
                is_approved=True).order_by('relevance')
        if 'link_type' in data and data['link_type'] != 'any':
            relevant_material_elements = relevant_material_elements.filter(
                material_element_type=data['link_type'])
            relevant_classified_occurrences = relevant_classified_occurrences.filter(
                occurrence_type=data['link_type']).filter(is_approved=True).order_by('relevance')
        contents = []
        if 'number_of_responses' not in data:
            len_contents = min(1, len(relevant_material_elements) + len(relevant_classified_occurrences))
        elif data['number_of_responses'] == 0:
            len_contents = len(relevant_material_elements) + len(relevant_classified_occurrences)
        else:
            len_contents = min(data['number_of_responses'],
                               len(relevant_material_elements) + len(relevant_classified_occurrences))
        for i in range(0, len_contents):
            if i < len(relevant_material_elements):
                contents.append(create_html_snippet(relevant_material_elements[i].ontology_term,
                                                    relevant_material_elements[i].content))
                MEUsage.objects.create(material_element=relevant_material_elements[i], usage_time=datetime.now())
            else:
                j = i - len(relevant_material_elements)
                contents.append(create_html_snippet(relevant_classified_occurrences[j].occurrence.ontology_term.term,
                                                    relevant_classified_occurrences[j].snippet))
                COUsage.objects.create(classified_occurrence=relevant_classified_occurrences[j],
                                       usage_time=datetime.now())

        return Response(contents)


def create_html_snippet(term, snippet):
    with open('./static/scaffolding_response.html', 'r') as f:
        file_text = f.read()
        return file_text.replace('{{ term }}', term).replace('{{ snippet }}', snippet)
