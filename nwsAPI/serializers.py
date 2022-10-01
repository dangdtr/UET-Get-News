from rest_framework import serializers
from .models import Nws, StpNws


class NwsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nws
        fields = '__all__' # importing all fields
 
class StpNwsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StpNws
        fields = '__all__' # importing all fields    