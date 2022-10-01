import os
from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
import json
import requests

import requests
from requests.adapters import HTTPAdapter, Retry

from nwsAPI.models import Nws

from .models import Subscriber
from .serializers import SubscriberSerializer
from rest_framework import generics


from chatbotAPI.messenger import Messenger, messages, attachments, templates, elements

# os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
VERYFY_TOKEN = 'uetgetnews'


class ListSubscriberView(generics.ListAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


class ChatBotView(generic.View):
    messenger = Messenger(access_token=ACCESS_TOKEN)

    def get(self, request):
        if not request.GET:
            return HttpResponse("Empty. This url used to verify.")

        if request.GET['hub']['mode'] == "subscribe" and request.GET['hub']['challenge']:
            if request.GET['hub']['verify_token'] == VERYFY_TOKEN:
                return HttpResponse(request.GET['hub']['challenge'])
            else:
                return HttpResponse('Verification token mismatch')
        return HttpResponse("Nothing")

    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)

        if "object" in data:
            if data["object"] == "page":

                for entry in data["entry"]:
                    for messaging_event in entry["messaging"]:

                        sender_id = messaging_event["sender"]["id"]

                        if messaging_event.get("message"):

                            if Subscriber.objects.filter(user_id=sender_id).filter(is_subscribed=True).exists():
                                template = self.create_subcribed_message_template(
                                    sender_id)
                                self.send_message(sender_id, template)

                            else:
                                template = self.create_begin_message_template(
                                    sender_id)
                                self.send_message(sender_id, template)

                        if messaging_event.get("postback"):
                            # TODO: send noti
                            # print("postback")
                            # if messaging_event["postback"]["payload"] == "LATEST_NEWS":
                            #     # global handler

                            #     nws = Nws.objects.filter(id=0).get()
                            #     template = self.create_message_template(nws.title(), nws.nws_url, nws.img_url,
                            #                                                 nws['subtitle'])
                            #     self.send_message(sender_id, template)

                            if messaging_event["postback"]["payload"] == "SIGNUP":
                                if not Subscriber.objects.filter(user_id=sender_id).exists():
                                    user_info = self.get_user_info(sender_id)
                                    Subscriber.objects.create(
                                        user_id=sender_id,
                                        first_name=user_info['first_name'],
                                        last_name=user_info['last_name'],
                                        is_subscribed=True
                                    )
                                    template = self.create_text_message_template(
                                        "Cảm ơn bạn đã đăng ký <3")
                                    self.send_message(sender_id, template)

                                else:
                                    Subscriber.objects.filter(
                                        user_id=sender_id).update(is_subscribed=True)
                                    template = self.create_text_message_template(
                                        "Hi. Bạn đã đăng ký rồi <3")
                                    self.send_message(sender_id, template)

                                template = self.create_menu_template(sender_id)
                                self.send_message(sender_id, template)

                            if messaging_event["postback"]["payload"] == "CANCEL":
                                if Subscriber.objects.filter(user_id=sender_id).filter(is_subscribed=False).exists():
                                    template = self.create_text_message_template(
                                        "Bạn đã huỷ Nhận tin tự động <3")
                                    self.send_message(sender_id, template)

                                else:
                                    Subscriber.objects.filter(
                                        user_id=sender_id).update(is_subscribed=False)

                                    template = self.create_text_message_template(
                                        "Bạn đã huỷ Nhận tin tự động. Cảm ơn bạn đã sử dụng <3")
                                    self.send_message(sender_id, template)

                                template = self.create_menu_template(sender_id)
                                self.send_message(sender_id, template)

        return HttpResponse("OK")

    def create_begin_message_template(self, user_id):
        info = self.get_user_info(user_id)
        latest_news_postback_button = elements.PostbackButton(
            title='Tin mới nhất',
            payload='LATEST_NEWS'
        )
        signup_postback_button = elements.PostbackButton(
            title='Đăng ký nhận tin',
            payload='SIGNUP'
        )

        template = templates.ButtonTemplate(
            text=f'Chào mừng {info["first_name"]} {info["last_name"]} đến với UET News.',
            buttons=[
                latest_news_postback_button, signup_postback_button
            ]
        )

        return template

    def create_subcribed_message_template(self, user_id):
        info = self.get_user_info(user_id)
        latest_news_postback_button = elements.PostbackButton(
            title='Tin mới nhất',
            payload='LATEST_NEWS'
        )
        cancel_postback_button = elements.PostbackButton(
            title='Huỷ đăng ký nhận tin.',
            payload='CANCEL'
        )

        template = templates.ButtonTemplate(
            text=f'Chào mừng {info["first_name"]} {info["last_name"]} đến với UET News.',
            buttons=[
                latest_news_postback_button, cancel_postback_button
            ]
        )

        return template

    def create_menu_template(self, user_id):
        latest_news_postback_button = elements.PostbackButton(
            title='Tin mới nhất',
            payload='LATEST_NEWS'
        )
        if Subscriber.objects.filter(user_id=user_id).filter(is_subscribed=True).exists():
            optional_postback_button = elements.PostbackButton(
                title='Huỷ đăng ký nhận tin.',
                payload='CANCEL'
            )
        else:
            optional_postback_button = elements.PostbackButton(
                title='Đăng ký nhận tin',
                payload='SIGNUP'
            )

        template = templates.ButtonTemplate(
            text='Menu',
            buttons=[
                latest_news_postback_button, optional_postback_button
            ]
        )
        return template

    def create_text_message_template(self, text):
        rich_roll = elements.Element(
            title=text,
            subtitle='Đừng ấn vào đây nhé',
            item_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=27s",
        )

        template = templates.GenericTemplate(
            elements=[rich_roll]
        )
        return template

    def create_message_template(self, title, url, img_url, subtitle):
        web_button = elements.WebUrlButton(
            title='Xem chi tiết',
            url=url
        )

        img_element = elements.Element(
            title=title,
            image_url=img_url,
            item_url=url,
            subtitle=subtitle,
            buttons=[
                web_button
            ]
        )

        template = templates.GenericTemplate(
            elements=[img_element]
        )

        return template

    def send_message(self, recipient_id, template):
        recipient = messages.Recipient(recipient_id=recipient_id)
        attachment = attachments.TemplateAttachment(template=template)

        message = messages.Message(attachment=attachment)
        request = messages.MessageRequest(recipient, message)

        self.messenger.send(request)

    def get_user_info(self, user_id):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        info = requests.get(
            f'https://graph.facebook.com/v15.0/{user_id}?fields=first_name,last_name,profile_pic&access_token={ACCESS_TOKEN}')
        return info.json()


def json_to_file(filename, data):
    with open(f"{filename}.json", "w") as outfile:
        outfile.write(json.dumps(data, indent=4))
