import requests
import json
from pprint import pprint
import environ, os
environ.Env.read_env('../.env')
env = environ.Env()

api = 'https://www.googleapis.com/books/v1/volumes?q=intitle:'
"""
url = api + "星の子"
res = requests.get(url).json()
n = res['totalItems']
item = res['items'][0]['volumeInfo']
pprint(item)
title = item['title']
first_author = item['authors'][0]
pub_date = item['publishedDate']
pub_year = pub_date.split("-")[0]
genre = item['categories'][0]
img_path = item['imageLinks']['thumbnail']
summary = item['description']
print(n)
print({"title": title, "first_author": first_author, "pub_year": pub_year, "genre": genre, "img_path": img_path, "summary": summary})
"""
def get_book_info(title, author=""):
    url = api + str(title)
    if author != "":
        url += "+inauthor:"
        url += author
    url += f'&key={env("GOOGLE_BOOKS_API_KEY")}' 
    res = requests.get(url).json()
    pprint(res)
    n = res['totalItems']
    item = res['items'][0]['volumeInfo']
    pprint(item)
    title = item['title']
    try:
        first_author = item['authors'][0]
    except:
        first_author = ""
    pub_date = item['publishedDate']
    pub_year = pub_date.split("-")[0]
    try:
        genre = item['categories'][0]
    except:
        genre = "Others"
    try:
        img_path = item['imageLinks']['thumbnail']
    except:
        img_path = ""
    try:
        summary = item['description']
        summary += '\n(Retrieved from Google Books.)'
    except:
        summary = ""
    print({"title": title, "first_author": first_author, "pub_year": pub_year, "genre": genre, "img_path": img_path, "summary": summary})
    return {"title": title, "first_author": first_author, "pub_year": pub_year, "genre": genre, "img_path": img_path, "summary": summary}

# print(get_book_info('社会学'))