from rest_framework import serializers
from .models import WastageRecord

class WastageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WastageRecord
        fields = '__all__'
