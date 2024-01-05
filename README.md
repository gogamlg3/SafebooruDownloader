A simple script for downloading images from safebooru.org

The script takes four arguments as input:
- link to site with search by tags
- page to start downloading from
- page to finish downloading from
- download path (optional)

install dependencies:
```
# pip install -r requirements.txt
```

Example:

Download only first page and save files in to "save" folder
```
# python download.py "https://safebooru.org/index.php?page=post&s=list&tags=makise_kurisu" 1 1 -d save
```

Download first and second page
```
# python download.py "https://safebooru.org/index.php?page=post&s=list&tags=makise_kurisu" 1 2
```