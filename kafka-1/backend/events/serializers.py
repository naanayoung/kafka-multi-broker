from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'  # include all of fields
