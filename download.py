from bs4 import BeautifulSoup
import requests
import wget
import argparse
import sys
import os
import re
import threading
from time import sleep, time

parser = argparse.ArgumentParser()
parser.add_argument('url', type=str, help='url from safebooru')
parser.add_argument('first_page', type=int, help='first page')
parser.add_argument('last_page', type=int, help='last page')
parser.add_argument('-d', '--directory', type=str, default='images', help='download path')
args = parser.parse_args()

os.makedirs(args.directory, exist_ok=True)

pid = args.first_page * 42 - 42
last_pid = args.last_page * 42 - 42
images_count = 0
site = args.url.split("//")[1].split("/")[0]

def timer(time_format='s', out_string="Время выполнения:"): # декоратор для замерки времени работы функций
    def decorator(func):
        def output_func(*args, **kwargs):
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            
            func_time = end_time - start_time
            
            if time_format == 'ms':
                func_time *= 1000
                print(f"{out_string} {func_time:.2f} ms")

            elif time_format == 's':
                print(f"{out_string} {func_time:.2f} s")
            
            return result
        return output_func
    return decorator

@timer('ms', "Время парсинга страницы:")
def get_thumbs(pid):  # получение tuple состоящий из массива id картинок
    if args.url[-5:] == 'pid=0':  # проверка на наличии pid в ссылке и отсечение этого запроса
        url = f'{args.url[0:-6]}&pid={pid}'
    else:
        url = f'{args.url}&pid={pid}'
    
    images = []
    while len(images) == 0: # проверка на пустую страницу в следствие перегрузки поиска
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        images = soup.findAll('span', class_='thumb')

    return images

def download_image(image):
    img_id = image.get('id')[1:]
    global images_count
    url = f"https://{site}/index.php?page=post&s=view&id={img_id}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
        
    li_list = soup.findAll('li')
    for i in li_list:
        if re.search("Original", i.get_text()) != None:       #фикс того, что скрипт не может найти li, содержащий "Original image"
            original_href = i.select('a[href]')[0].get('href')
            break
        
    file_extension = ""
    original_href = original_href.split("?")[0]
    for i in range(len(original_href)-1, 0, -1):
        if original_href[i] != '.':
            file_extension += original_href[i]

        else:
            file_extension = file_extension[::-1]
            break

    output_path = f"{args.directory}/{img_id}.{file_extension}"
    if os.path.isfile(output_path) == False:
        wget.download(original_href, out=output_path, bar=None)
        print(f"downloaded: {img_id}.{file_extension}")
        images_count += 1

    else:
        print(f'{img_id}.{file_extension} is already downloaded')

while pid <= last_pid:
    images = get_thumbs(pid)
    threads = []

    for image in images:
        threads.append(threading.Thread(target=download_image, args=(image, )))

    for t in threads:
        t.start()
        sleep(0.25)
        
    for t in threads:
        t.join()

    pid += 42

print(f'Successfully downloaded {images_count} images')