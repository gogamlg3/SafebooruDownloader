from bs4 import BeautifulSoup
import requests
import wget
import sys
import os

if len(sys.argv) == 5:
    try:
        os.mkdir(sys.argv[4])

    except:
        pass

def get_thumbs(pid):
    if sys.argv[1][-5:] == 'pid=0':
        url = f'{sys.argv[1][0:-6]}&pid={pid}'

    else:
        url = f'{sys.argv[1]}&pid={pid}'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    images = soup.findAll('span', class_='thumb')

    if images == 0:
        get_thumbs(pid)

    else:
        return images

pid = int(sys.argv[2]) * 40 - 40
last_pid = int(sys.argv[3]) * 40 - 40
images_count = 0

while pid <= last_pid:
    images = get_thumbs(pid)

    for image in images:
        img_id = image.get('id')[1:]
        url = f'https://safebooru.org/index.php?page=post&s=view&id={img_id}'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        original_href = soup.findAll('li', string='Original image')[0].select('a[href]')[0].get('href')

        if original_href[-3:] == 'peg':
            file_extension = original_href[-4:]

        else:
            file_extension = original_href[-3:]

        if len(sys.argv) == 5:
            output_path = f'{sys.argv[4]}/{img_id}.{file_extension}'
 
        else:
            output_path = f'{img_id}.{file_extension}'

        try:
            if os.path.isfile(output_path) == False:
                wget.download(original_href, out=output_path, bar=None)
                print(f"downloaded: {img_id}.{file_extension}")
                images_count += 1
            else:
                print(f'{img_id}.{file_extension} is already downloaded')

        except Exception as e:
            print(f"error: {e}")

    pid += 40

print(f'Successfully downloaded {images_count} files')
