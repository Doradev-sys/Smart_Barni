from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True, default='')
    class Meta:
        model = Alert
        fields = '__all__'
