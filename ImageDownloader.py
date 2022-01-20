import random
import string
import requests
import shutil
from bs4 import BeautifulSoup

random_strings = []
base_url = "https://prnt.sc/"
save_path = r"D:\code\PrntScnImages\\"

for i in range(1000):
    rand_text = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    random_strings.append(rand_text)

print(random_strings)

for i in random_strings:
    image_url = base_url + i
    filename = save_path + i + '.png'

    r = requests.get(image_url,
                     headers={'User-Agent': 'Chrome)'},
                     stream=True)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        img_elements = soup.find_all("img", {"class": "no-click screenshot-image"})

        for image in img_elements:
            image_url = image['src']

            if 'http' not in image_url:
                image_url = 'http:' + image['src']
                s = requests.get(image_url,
                                 headers={'User-Agent': 'Chrome)'},
                                 stream=True)
            else:
                s = requests.get(image_url,
                                 headers={'User-Agent': 'Chrome)'},
                                 stream=True)

            if s.status_code == 200 and s.headers['Content-Length'] != '4267':
                s.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(s.raw, f)

                print('Image successfully Downloaded: ', filename)
            else:
                print('Image could not be retrieved')
    else:
        print('Page could not be retrieved')
