from rest_framework import generics
from .models import Nws, StpNws
from .serializers import NwsSerializer, StpNwsSerializer

class ListNwsView(generics.ListAPIView):
    queryset = Nws.objects.all() # used for returning objects from this view
    serializer_class = NwsSerializer

    
class ListStpNwsView(generics.ListAPIView):
    queryset = StpNws.objects.all() # used for returning objects from this view
    serializer_class = StpNwsSerializer
    
    # def get(self, request):
        # nws = StpNws.objects.filter(id=0).get()
        # template = messenger.create_message_template(nws.title(), nws.nws_url, nws.img_url,
        #                                             nws['subtitle'])
        # self.messenger.send_message(sender_id, template)

