import os
from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
import json

import requests
from requests.adapters import HTTPAdapter, Retry

from nwsAPI.models import Nws, StpNws

from .models import Subscriber
from .serializers import SubscriberSerializer
from rest_framework import generics

from chatbotAPI.messenger import Messenger


ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
VERYFY_TOKEN = 'uetgetnews'


class ListSubscriberView(generics.ListAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


messenger = Messenger(access_token=ACCESS_TOKEN)


class ChatBotView(generic.View):

    def get(self, request):
        if 'hub.mode' not in request.GET:
            stp_nws = StpNws.objects.values()
            sub_list = Subscriber.objects.filter(is_subscribed=True).values()

            for nws in stp_nws:

                template = messenger.create_message_template(nws['title'], nws['nws_url'], nws['img_url'],
                                                             'subtitle')

                for sub in sub_list:
                    messenger.send_message(sub['user_id'], template)
                    print(f"Send to {sub['first_name']} {sub['last_name']}")

            return HttpResponse("Empty. This url used to verify.")

        if request.GET['hub.mode'] == "subscribe" and request.GET['hub.challenge']:
            if request.GET['hub.verify_token'] == VERYFY_TOKEN:
                return HttpResponse(request.GET['hub.challenge'])
            else:
                return HttpResponse('Verification token mismatch')
        return HttpResponse("Nothing")

    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        # TODO: handling with message queue
        if "object" in data:
            if data["object"] == "page":

                for entry in data["entry"]:
                    for messaging_event in entry["messaging"]:

                        sender_id = messaging_event["sender"]["id"]

                        if messaging_event.get("message"):

                            if Subscriber.objects.filter(user_id=sender_id).filter(is_subscribed=True).exists():
                                template = messenger.create_subcribed_message_template(
                                    sender_id)
                                messenger.send_message(sender_id, template)

                            else:
                                template = messenger.create_begin_message_template(
                                    sender_id)
                                messenger.send_message(sender_id, template)

                        if messaging_event.get("postback"):
                            # TODO: send noti
                            # print("postback")
                            if messaging_event["postback"]["payload"] == "LATEST_NEWS":

                                nws = Nws.objects.filter(id=0).get()
                                template = messenger.create_message_template(nws.title, nws.nws_url, nws.img_url,
                                                                             'subtitle')
                                messenger.send_message(sender_id, template)

                            if messaging_event["postback"]["payload"] == "SIGNUP":
                                if not Subscriber.objects.filter(user_id=sender_id).exists():
                                    user_info = messenger.get_user_info(
                                        sender_id)
                                    Subscriber.objects.create(
                                        user_id=sender_id,
                                        first_name=user_info['first_name'],
                                        last_name=user_info['last_name'],
                                        is_subscribed=True
                                    )
                                    template = messenger.create_text_message_template(
                                        "Cảm ơn bạn đã đăng ký <3")
                                    messenger.send_message(sender_id, template)

                                else:
                                    Subscriber.objects.filter(
                                        user_id=sender_id).update(is_subscribed=True)
                                    template = messenger.create_text_message_template(
                                        "Hi. Bạn đã đăng ký rồi <3")
                                    messenger.send_message(sender_id, template)

                                is_subscribed = Subscriber.objects.filter(
                                    user_id=sender_id).filter(is_subscribed=True).exists()
                                template = messenger.create_menu_template(
                                    sender_id, is_subscribed)
                                messenger.send_message(sender_id, template)

                            if messaging_event["postback"]["payload"] == "CANCEL":
                                if Subscriber.objects.filter(user_id=sender_id).filter(is_subscribed=False).exists():
                                    template = messenger.create_text_message_template(
                                        "Bạn đã huỷ Nhận tin tự động <3")
                                    messenger.send_message(sender_id, template)

                                else:
                                    Subscriber.objects.filter(
                                        user_id=sender_id).update(is_subscribed=False)

                                    template = messenger.create_text_message_template(
                                        "Bạn đã huỷ Nhận tin tự động. Cảm ơn bạn đã sử dụng <3")
                                    messenger.send_message(sender_id, template)

                                is_subscribed = Subscriber.objects.filter(
                                    user_id=sender_id).filter(is_subscribed=True).exists()
                                template = messenger.create_menu_template(
                                    sender_id, is_subscribed)
                                messenger.send_message(sender_id, template)

        return HttpResponse("OK")


def json_to_file(filename, data):
    with open(f"{filename}.json", "w") as outfile:
        outfile.write(json.dumps(data, indent=4))
