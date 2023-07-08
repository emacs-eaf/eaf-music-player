import random
import requests
import hashlib
from typing import Optional
from music_service.utils import USER_AGENT
from music_service.base import BaseSongProvider

default_headers = {
    'User-Agent': USER_AGENT,
    'Referer': 'http://www.kuwo.cn/'
}

def generate_kw_token(length=32):
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choices(charset, k=length))

class KuWo(BaseSongProvider):
    provider_name = 'kuwo'

    def fetch_song_url(self, name: str, artist: str = '', album: str = ''):
        token = generate_kw_token()
        cross = hashlib.md5(token.encode('utf-8')).hexdigest()
        keyword = f'{name} {artist}'
        song_id = self.api_search_song_id(keyword, token, cross)
        if not song_id:
            return None
        return self.api_get_song_url(song_id, token, cross)

    def _api_request(self, url, params, token, cross):
        headers = default_headers.copy()
        headers['Cross'] = cross
        headers['Cookie'] = f'Hm_token={token}'
        return requests.get(url, params=params, headers=headers).json()

    def api_search_song_id(self, keyword: str, token: str, cross: str) -> int:
        url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord'
        params = {
            'key': keyword,
            'pn': 1,
            'rn': 30,
            'httpsStatus': 1
        }
        resp = self._api_request(url, params, token, cross)
        lists = resp.get('data', {}).get('list', None)
        if not lists:
            return 0
        return lists[0].get('rid', 0)


    def api_get_song_url(self, song_id: int, token: str, cross: str) -> Optional[str]:
        url = 'http://www.kuwo.cn/api/v1/www/music/playUrl'
        params = {
            'mid': song_id,
            'type': 'music',
            'httpsStatus': 1,
            'plat': 'web_www'
        }
        resp = self._api_request(url, params, token, cross)
        return resp.get('data', {}).get('url', None)
