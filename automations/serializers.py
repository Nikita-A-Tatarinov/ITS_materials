from rest_framework import serializers

from automations.models import COUsage


class COUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = COUsage
        fields = '__all__'
