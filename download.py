from bs4 import BeautifulSoup
import requests
import wget
import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument('url', type=str, help='url from safebooru')
parser.add_argument('first_page', type=int, help='first page')
parser.add_argument('last_page', type=int, help='last page')
parser.add_argument('-d', '--directory', type=str, default='images', help='download path')
args = parser.parse_args()

os.makedirs(args.directory, exist_ok=True) 

def get_thumbs(pid):
    if args.url[-5:] == 'pid=0':
        url = f'{args.url[0:-6]}&pid={pid}'
    else:
        url = f'{args.url}&pid={pid}'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    images = soup.findAll('span', class_='thumb')

    if images == 0:
        get_thumbs(pid)
    else:
        return images

def download(original_href, output_path, img_id, file_extension):
    global images_count
    wget.download(original_href, out=output_path, bar=None)
    print(f"downloaded: {img_id}.{file_extension}")
    images_count += 1

pid = args.first_page * 40 - 40
last_pid = args.last_page * 40 - 40
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

        output_path = f'{args.directory}/{img_id}.{file_extension}'

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

print(f'Successfully downloaded {images_count} images')
