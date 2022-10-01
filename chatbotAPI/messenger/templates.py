

class GenericTemplate(object):

    template_type = 'generic'

    def __init__(self, elements):
        self.elements = elements

    def to_dict(self):
        return {
            'template_type': self.template_type,
            'elements': [
                element.to_dict() for element in self.elements
            ]
        }


class ButtonTemplate(object):

    template_type = 'button'

    def __init__(self, text, buttons):
        self.text = text
        self.buttons = buttons

    def to_dict(self):
        return {
            'template_type': self.template_type,
            'text': self.text,
            'buttons': [
                button.to_dict() for button in self.buttons
            ]
        }
