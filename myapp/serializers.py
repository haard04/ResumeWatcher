# serializers.py
from rest_framework import serializers
from .models import Job,MyModel

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job,MyModel
        fields = '__all__'
