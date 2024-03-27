import random
import numpy as np
import string
import requests
import shutil
import os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

images_desired = 100
# random_strings = set()
base_url = "https://prnt.sc/"
save_path = r"C:\repo\ImageDownloader\ImageDownloader\PrntScnImages\\"
removed_image_path = r"C:\repo\ImageDownloader\ImageDownloader\PrntScnImages\assets\screenshot_removed.png"
imgur_not_available = r"C:\repo\ImageDownloader\ImageDownloader\PrntScnImages\assets\imgur_not_available.png"
existing_screenshots = os.listdir(save_path)
existing_screenshots = [screenshot[0:-4] for screenshot in existing_screenshots]
tried_strings_path = r"C:\repo\ImageDownloader\ImageDownloader\PrntScnImages\assets\random_strings.txt"


def is_removed_image(downloaded_image_response):
    prnt_sc_removed_image = Image.open(removed_image_path)
    imgur_removed_image = Image.open(imgur_not_available)
    downloaded_image = Image.open(BytesIO(downloaded_image_response.content))

    # Convert images to arrays and compare
    arr1 = np.array(prnt_sc_removed_image)
    arr2 = np.array(imgur_removed_image)
    arr3 = np.array(downloaded_image)
    is_imgur_removed = np.array_equal(arr3, arr2)
    is_prntsc_removed = np.array_equal(arr3, arr1)
    return is_prntsc_removed or is_imgur_removed


tried_strings = []

# Open the file in read mode
with open(tried_strings_path, 'r') as file:
    # Read each line in the file
    for line in file:
        # Remove the newline character at the end of each line and add the line to the list
        tried_strings.append(line.strip())

# i = 0
# while i < 1000:  # make us 1000 new strings
#     rand_text = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
#     if rand_text not in existing_screenshots and rand_text not in random_strings and rand_text not in tried_strings:
#         random_strings.add(rand_text)
#         i += 1

# print(random_strings)

# with open(tried_strings_path, 'a') as file:
#     # Iterate through each element in the list
#     for element in random_strings:
#         # Write the element to the file followed by a newline character
#         file.write(element + '\n')
i = 0
while i < images_desired:
    rand_text = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    while rand_text in existing_screenshots and rand_text not in random_strings and rand_text not in tried_strings:
        rand_text = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    image_url = base_url + rand_text
    filename = save_path + rand_text + '.png'

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
                    with open(tried_strings_path, 'a') as file:
                        file.write(rand_text + '\n')
                    i += 1
            else:
                print('Image could not be retrieved')
    else:
        print('Page could not be retrieved')

print('downloaded ' + str(images_desired) + ' images!')
