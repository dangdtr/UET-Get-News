import requests
from messengerbot import messages, attachments, templates, elements
from requests.adapters import HTTPAdapter, Retry


class Messenger:
    GRAPH_API_URL = 'https://graph.facebook.com/v15.0/me'

    def __init__(self, access_token):
        self.access_token = access_token

    def send(self, message):
        params = {
            'access_token': self.access_token
        }

        response = requests.post(
            f'{self.GRAPH_API_URL}/messages',
            params=params,
            json=message.to_dict()
        )
        if response.status_code != 200:
            print("Error!")
        return response.json()

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

    def create_menu_template(self, user_id, is_subscribed):
        latest_news_postback_button = elements.PostbackButton(
            title='Tin mới nhất',
            payload='LATEST_NEWS'
        )
        if is_subscribed:
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
                web_button,
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

        return self.send(request)

    def get_user_info(self, user_id):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        info = requests.get(
            f'https://graph.facebook.com/v15.0/{user_id}?fields=first_name,last_name,profile_pic&access_token={self.access_token}')
        return info.json()