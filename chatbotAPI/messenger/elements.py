

class Element(object):

    def __init__(self, title, item_url=None,
                 image_url=None, subtitle=None, buttons=None):

        self.title = title
        self.item_url = item_url
        self.image_url = image_url
        self.subtitle = subtitle
        self.buttons = buttons

    def to_dict(self):
        serialized = {
            'title': self.title,
            'item_url': self.item_url,
            'image_url': self.image_url,
            'subtitle': self.subtitle
        }
        if self.buttons:
            serialized['buttons'] = [
                button.to_dict() for button in self.buttons
            ]
        return serialized

class Button(object):

    def __init__(self, title):
        self.title = title

    def to_dict(self):
        serialized = {
            'type': self.button_type,
            'title': self.title
        }
        if self.button_type == 'web_url':
            serialized['url'] = self.url
        elif self.button_type == 'postback':
            serialized['payload'] = self.payload
        return serialized


class WebUrlButton(Button):

    button_type = 'web_url'

    def __init__(self, title, url):
        self.url = url
        super(WebUrlButton, self).__init__(title=title)


class PostbackButton(Button):

    button_type = 'postback'

    def __init__(self, title, payload):
        self.payload = payload
        super(PostbackButton, self).__init__(title=title)
