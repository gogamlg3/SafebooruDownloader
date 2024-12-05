from bs4 import BeautifulSoup
import requests
import wget
import os
import re
import threading
from time import sleep
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Создание GUI
class SafebooruDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Safebooru Downloader")
        self.root.geometry("640x480")
        
        self.url = tk.StringVar()
        self.first_page = tk.IntVar(value=1)
        self.last_page = tk.IntVar(value=1)
        self.directory = tk.StringVar(value="images")
        
        self.create_widgets()
    
    def create_widgets(self):
        ttk.Label(self.root, text="URL:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.url, width=50).grid(row=0, column=1, pady=5, sticky="w")
        
        ttk.Label(self.root, text="First Page:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.first_page, width=10).grid(row=1, column=1, pady=5, sticky="w")
        
        ttk.Label(self.root, text="Last Page:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.last_page, width=10).grid(row=2, column=1, pady=5, sticky="w")
        
        ttk.Label(self.root, text="Save Directory:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.directory, width=50).grid(row=3, column=1, pady=5, sticky="w")
        ttk.Button(self.root, text="Browse", command=self.select_directory).grid(row=3, column=2, padx=5)
        
        ttk.Button(self.root, text="Start Download", command=self.start_download).grid(row=4, column=1, pady=20)
        
        self.output_text = tk.Text(self.root, wrap="word", height=15, width=70)
        self.output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
    
    def select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.directory.set(dir_path)
    
    def start_download(self):
        if not self.url.get() or self.first_page.get() <= 0 or self.last_page.get() < self.first_page.get():
            messagebox.showerror("Error", "Check input")
            return
        
        os.makedirs(self.directory.get(), exist_ok=True)
        
        threading.Thread(target=self.download_images, daemon=True).start()
    
    def download_images(self):
        pid = self.first_page.get() * 42 - 42
        last_pid = self.last_page.get() * 42 - 42
        site = self.url.get().split("//")[1].split("/")[0]
        
        while pid <= last_pid:
            images = self.get_thumbs(pid)
            threads = []

            for image in images:
                threads.append(threading.Thread(target=self.download_image, args=(image, site, self.directory.get())))

            for t in threads:
                t.start()
                sleep(0.5)
            
            for t in threads:
                t.join()
            
            pid += 42
        
        self.log_output("Download complete.")
    
    def get_thumbs(self, pid):
        if self.url.get()[-5:] == 'pid=0':
            url = f'{self.url.get()[0:-6]}&pid={pid}'
        else:
            url = f'{self.url.get()}&pid={pid}'
        
        images = []
        while len(images) == 0:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            images = soup.findAll('span', class_='thumb')
        
        return images
    
    def download_image(self, image, site, directory):
        img_id = image.get('id')[1:]
        url = f"https://{site}/index.php?page=post&s=view&id={img_id}"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        
        li_list = soup.findAll('li')
        for i in li_list:
            if re.search("Original", i.get_text()) is not None:
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
        
        output_path = f"{directory}/{img_id}.{file_extension}"
        if not os.path.isfile(output_path):
            wget.download(original_href, out=output_path, bar=None)
            self.log_output(f"downloaded: {img_id}.{file_extension}")
        else:
            self.log_output(f"{img_id}.{file_extension} is already downloaded")
    
    def log_output(self, message):
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SafebooruDownloader(root)
    root.mainloop()
