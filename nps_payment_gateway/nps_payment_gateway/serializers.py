from rest_framework import serializers
from .models import NpsPayment

class NpsPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NpsPayment
        fields = '__all__'
