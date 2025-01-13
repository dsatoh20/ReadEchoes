import requests
import json
from pprint import pprint
import environ, os
environ.Env.read_env('../.env')
env = environ.Env()

ACCESS_TOKEN = env("TMDB_ACCESS_TOKEN")

class TMDB:
    def __init__(self, token):
        self.token = token
        self.headers_ = {'accept': 'application/json', 'Authorization': f'Bearer {self.token}'}        
        self.base_url_ = 'https://api.themoviedb.org/3/'
        self.img_base_url_ = 'https://image.tmdb.org/t/p/w500'

    def _json_by_get_request(self, url, params={}):
        res = requests.get(url, headers=self.headers_, params=params)
        pprint(self.headers_)
        print(res.url)
        return json.loads(res.text)

    def search_movies(self, query): # タイトルで検索
        params = {'query': query}
        url = f'{self.base_url_}search/movie'
        return self._json_by_get_request(url, params)                    

    def get_movie(self, movie_id): # idで検索
        url = f'{self.base_url_}movie/{movie_id}'
        return self._json_by_get_request(url)

    def get_movie_credits(self, movie_id): # クレジットを取得
        url = f'{self.base_url_}movie/{movie_id}/credits'
        return self._json_by_get_request(url)   

    def get_movie_images(self, movie_id, language=None): # ポスター画像を取得
        url = f'{self.base_url_}movie/{movie_id}/images'
        return self._json_by_get_request(url)        

    def get_movie_release_dates(self, movie_id): # 公開日を取得
        url = f'{self.base_url_}movie/{movie_id}/release_dates'
        return self._json_by_get_request(url)
    
"""
api = TMDB(ACCESS_TOKEN)
res = api.search_movies("RRR")
pprint(res)
movie_id = res['results'][0]['id']
all = api.get_movie(movie_id)
print("全部", all)
credits = api.get_movie_credits(movie_id)
crews = credits['crew']
i = 0
while True:
    if crews[i]['known_for_department'] == 'Directing':
        director = crews[i]['name']
        break
    i+=1
print("監督", director)
imgs = all['poster_path']
print("画像", imgs)
print(f"<img src={api.img_base_url_}{imgs}>")
date = all['release_date']
print("公開日", date)
genre = all['genres'][0]['name']
print("ジャンル", genre)
overview = all['overview']
print("あらすじ", overview)
"""

def get_movie_info(title):
    # 監督、ポスター、公開日、ジャンル、あらすじを取得
    api = TMDB(ACCESS_TOKEN)
    # titleで検索、一番にヒットしたものを採用
    res = api.search_movies(title)
    pprint(res)
    movie_id = res['results'][0]['id'] # idを取得
    all = api.get_movie(movie_id)
    # 監督 --> director
    credits = api.get_movie_credits(movie_id)
    crews = credits['crew']
    i = 0
    while True:
        if crews[i]['known_for_department'] == 'Directing':
            director = crews[i]['name']
            break
        i+=1
    # ポスター --> imgtag
    imgs = all['poster_path']
    img_path = f"{api.img_base_url_}{imgs}"
    # 公開日 --> date
    date = all['release_date']
    pub_year = date.split('-')[0]
    # ジャンル --> genre
    genre = all['genres'][0]['name']
    # あらすじ --> overview
    overview = all['overview']
    overview += '\n(Retrieved from The Movie Database.)'
    return {'first_author': director, 'img_path': img_path, 'pub_year': pub_year, 'genre': genre, 'summary': overview}

# print(get_movie_info("きまじめ楽隊のぼんやり戦争"))