from rest_framework import serializers

from db_materials.models import MEUsage


class MEUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MEUsage
        fields = "__all__"


class ScaffoldingRequestSerializer(serializers.Serializer):
    ontology_term = serializers.CharField(max_length=255)
    distinction_ontology_term = serializers.CharField(max_length=255, required=False)
    link_type = serializers.CharField(max_length=255, required=False)
    number_of_responses = serializers.IntegerField(required=False)

    def validate_link_type(self, value):
        possible_values = ['any', 'definition', 'example', 'distinction', 'other']
        if value not in possible_values:
            raise serializers.ValidationError(f'Incorrect value of link type: should be one of {possible_values}')
        return value

    def validate_number_of_responses(self, value):
        if value < 0:
            raise serializers.ValidationError(f'Value of number of responses should be non-negative '
                                              f'(0 for when all links are required)')
        return value
