from rest_framework import generics
from .models import Nws, StpNws
from .serializers import NwsSerializer, StpNwsSerializer

class ListNwsView(generics.ListAPIView):
    queryset = Nws.objects.all() # used for returning objects from this view
    serializer_class = NwsSerializer

    
class ListStpNwsView(generics.ListAPIView):
    queryset = StpNws.objects.all() # used for returning objects from this view
    serializer_class = StpNwsSerializer

