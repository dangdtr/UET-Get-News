from email.policy import default
from django.db import models

# Create your models here.


class Subscriber(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.user_id
