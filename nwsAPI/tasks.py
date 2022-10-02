
from time import sleep
from celery import shared_task
from bs4 import BeautifulSoup
import requests
from .models import Nws, StpNws
import urllib3
from django.utils import timezone
from requests.adapters import HTTPAdapter, Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

started = False

URL = {"tin-sinh-vien": "https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/",
       "hoc-phi-hoc-bong": "https://uet.vnu.edu.vn/category/sinh-vien/hoc-phi-hoc-bong/",
       }

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


@shared_task
# some heavy stuff here
def create_nws():
    if len(Nws.objects.values()) == 0:
        print('Creating nws data ..', end=' ')

        while True:
            try:
                page = requests.get(
                    'https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/', verify=False)
                # print(page)
                break
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 120 seconds")
                print("ZZzzzz...")
                sleep(120)
                print("Was a nice sleep, now let me continue...")
                continue

        bs = BeautifulSoup(page.content, "html.parser")
        job_elements = bs.find_all("div", class_="item-thumbnail")
        idx = 0
        for element in job_elements:
            title = element.find("a")['title']
            nws_url = element.find("a")['href']
            img_url = element.find("img")['src']

            # create objects in database
            Nws.objects.create(
                id=idx,
                title=title,
                nws_url=nws_url,
                img_url=img_url,
            )
            idx += 1
            # sleep few seconds to avoid database block
            sleep(5)

    else:
        update_nws()

    print("Done!. Waiting 120s...")


@shared_task
# some heavy stuff here
def update_nws():
    print('Update nws data ...')

    while True:
        try:
            page = requests.get(
                'https://uet.vnu.edu.vn/category/tin-tuc/tin-sinh-vien/', verify=False)
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

    bs = BeautifulSoup(page.content, "html.parser")

    first_element = bs.find("div", class_="item-thumbnail")

    # Get first nws on website
    if first_element is not None:
        temp_first_title = first_element.find("a")['title']

        # Then compare with first in db
        if temp_first_title == Nws.objects.filter(id=0).get().title:
            print("Not detect change.")
        else:
            print("Detected change.")
            job_elements = bs.find_all("div", class_="item-thumbnail")

            saved_data = (Nws.objects.values())

            new_data = []

            idx = 0
            for element in job_elements:
                title = element.find("a")['title']
                nws_url = element.find("a")['href']
                img_url = element.find("img")['src']
                img_url = img_url.replace("2018", "2017").replace("01", "12")
                new_data.append({'id': idx, 'title': title, 'nws_url': nws_url,
                                'img_url': img_url, 'time': timezone.now()})
                idx += 1

            StpNws.objects.all().delete()

            idx = 0
            while new_data[idx]['title'] != saved_data[0]['title']:
                StpNws.objects.create(
                    id=idx,
                    title=new_data[idx]['title'],
                    nws_url=new_data[idx]['nws_url'],
                    img_url=new_data[idx]['nws_url'],
                )
                idx += 1
                sleep(5)

            # update nws to db
            for val in new_data:
                Nws.objects.filter(id=val['id']).update(**val)
    print("Done!. Waiting 120s...")


@shared_task
def send_noti():
    if len(StpNws.objects.values()) != 0:
        # data = StpNws.objects.values()
        print("Sent noti!")
        page = requests.get("http://localhost:8000/")

        # TODO:
        StpNws.objects.all().delete()


create_nws()

while True:
    sleep(120)
    update_nws()
    send_noti()
