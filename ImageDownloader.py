import random
import numpy as np
import string
import requests
import os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

images_desired = 100
base_url = "https://prnt.sc/"
save_path = r"C:\repo\ImageDownloader\PrntScnImages\\"
removed_image_path = r"C:\repo\ImageDownloader\assets\screenshot_removed.png"
imgur_not_available = r"C:\repo\ImageDownloader\assets\imgur_not_available.png"
existing_screenshots = os.listdir(save_path)
existing_screenshots = [screenshot[0:-4] for screenshot in existing_screenshots]
tried_strings_path = r"C:\repo\ImageDownloader\assets\random_strings.txt"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def is_removed_image(downloaded_image_response):
    prnt_sc_removed_image = Image.open(removed_image_path)
    imgur_removed_image = Image.open(imgur_not_available)
    downloaded_image = Image.open(BytesIO(downloaded_image_response.content))

    width, height = downloaded_image.size

    # Convert images to arrays and compare
    arr1 = np.array(prnt_sc_removed_image)
    arr2 = np.array(imgur_removed_image)
    arr3 = np.array(downloaded_image)
    is_imgur_removed = np.array_equal(arr3, arr2)
    is_prntsc_removed = np.array_equal(arr3, arr1)

    """
    looking for an exact image size is unfortunately one  of
    the only reliable ways to find these.
    """
    if width == 422 and height == 108:
        is_prntsc_removed = True

    return is_prntsc_removed or is_imgur_removed


tried_strings = []

# Open the file in read mode
with open(tried_strings_path, 'r') as file:
    # Read each line in the file
    for line in file:
        # Remove the newline character at the end of each line and add the line to the list
        tried_strings.append(line.strip())

i = 0
while i < images_desired:
    rand_text = generate_random_string(6)
    # keep generating random string until it is one we haven't done before
    while rand_text in existing_screenshots or rand_text in tried_strings:
        rand_text = generate_random_string(6)
        print(rand_text)

    image_url = base_url + rand_text
    filename = save_path + rand_text + '.png'

    r = requests.get(image_url,
                     headers={'User-Agent': 'Chrome)'},
                     stream=True)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        img_elements = soup.find_all("img", {"class": "no-click screenshot-image"})

        if len(img_elements) == 0:
            print('no screenshot')
            with open(tried_strings_path, 'a') as file:  # record that we tried this string
                file.write(rand_text + '\n')
            continue

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
                s2 = s
                # s.raw.decode_content = True
                if is_removed_image(s2):  # if the screenshot is the 'can't find image' image
                    print('screenshot removed')
                else:
                    img = Image.open(BytesIO(s2.content))
                    img.save(filename)
                    print('Image successfully Downloaded: ', filename)
                    # with open(filename, 'wb') as f:
                    #     shutil.copyfileobj(s.raw, f)
                    i += 1
                with open(tried_strings_path, 'a') as file:  # record that we tried this string
                    file.write(rand_text + '\n')
            else:
                print('Image could not be retrieved')
    else:
        print('Page could not be retrieved')

print('downloaded ' + str(images_desired) + ' images!')
