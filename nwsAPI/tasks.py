import os
from time import sleep
from celery import shared_task
from bs4 import BeautifulSoup
import requests

from chatbotAPI.messenger import Messenger
from chatbotAPI.models import Subscriber
from .models import Nws, StpNws
import urllib3
from django.utils import timezone
from requests.adapters import HTTPAdapter, Retry
from django.conf import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/feed/"
API_KEY = settings.API_KEY
IMG_URL = "https://uet.vnu.edu.vn/wp-content/uploads/2017/12/GetArticleImage.jpg"
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
VERYFY_TOKEN = 'uetgetnews'

messenger = Messenger(access_token=ACCESS_TOKEN)


@shared_task
# some heavy stuff here
def create_nws():
    if len(Nws.objects.values()) == 0:
        print('Creating nws data ..', end=' ')

        while True:
            try:
                page = requests.get(
                    'https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/feed/', verify=False)
                break
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 120 seconds")
                print("ZZzzzz...")
                sleep(120)
                print("Was a nice sleep, now let me continue...")
                continue

        bs = BeautifulSoup(page.content, "xml")
        idx = 0

        items = bs.find_all("item")
        for item in items:

            des = BeautifulSoup(item.description.text, features="lxml")
            destext = des.text.replace("\xa0", "").lstrip()
            title = item.find('title').text
            url = item.find("guid").text

            # create objects in database
            Nws.objects.create(
                id=idx,
                title=title,
                nws_url=url,
                img_url='https://uet.vnu.edu.vn/wp-content/uploads/2017/12/GetArticleImage.jpg',
                des=destext[:100]
            )
            idx += 1
            # sleep few seconds to avoid database block
            sleep(1)

    else:
        update_nws()

    print("\nDone!")


@shared_task
# some heavy stuff here
def update_nws():
    print('Update nws data ...')

    while True:
        try:
            page = requests.get(
                'https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/feed/', verify=False)
            if page.status_code == 200:
                break
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 120 seconds")
            print("ZZzzzz...")
            sleep(120)
            print("Was a nice sleep, now let me continue...")
            continue

    bs = BeautifulSoup(page.content, "xml")

    first_element = bs.find('item')

    # Get first nws on website
    if first_element is not None:
        temp_first_title = bs.find('item').find('title').text

        # Then compare with first in db
        if temp_first_title == Nws.objects.filter(id=0).get().title:
            print("Not detect change.")
        else:
            print("Detected change.")

            items = bs.find_all("item")

            saved_data = (Nws.objects.values())

            new_data = []

            idx = 0
            for item in items:
                print(type(item))
                des = BeautifulSoup(item.description.text, features="lxml")
                destext = des.text.replace("\xa0", "").lstrip()
                title = item.find('title').text
                url = item.find("guid").text

                # create objects in database
                new_data.append({'id': idx, 'title': title, 'nws_url': url,
                                'img_url': IMG_URL, 'des': destext[:100], 'time': timezone.now()})
                idx += 1

            StpNws.objects.all().delete()

            idx = 0
            while new_data[idx]['title'] != saved_data[0]['title']:
                StpNws.objects.create(
                    id=idx,
                    title=new_data[idx]['title'],
                    nws_url=new_data[idx]['nws_url'],
                    img_url=new_data[idx]['img_url'],
                    des=new_data[idx]['des']
                )
                idx += 1
                sleep(5)

            # update nws to db
            for val in new_data:
                Nws.objects.filter(id=val['id']).update(**val)
    print("Done!. Waiting 120...")


@shared_task
def send_noti():
    chat_id = "-1001569650376"
    if len(StpNws.objects.values()) != 0:
        data = Nws.objects.values()
        for val in data:
            url = val['nws_url']
            response = requests.get(
                f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={chat_id}&text={url}")
            print("Sent noti!: ", response.json())

            users = Subscriber.objects.values()
            for user in users:
                if user['is_subscribed'] == 1:
                    template = messenger.create_message_template(
                        val['title'], val['nws_url'], val['img_url'], val['des'])
                    messenger.send_message(user['user_id'], template)

        StpNws.objects.all().delete()


create_nws()

while True:
    sleep(120)
    update_nws()
    send_noti()
