import base64
import time
from typing import Optional
from urllib.parse import quote_plus

import requests

from music_service.base import BaseProvider


class QQMusicApi(BaseProvider):
    provider_name = 'qq'

    def fetch_lyric(self, name: str, artist: str = '', album: str = '') -> Optional[str]:
        result = self.api_search_song(name, artist, album)
        item_list = result.get('data', {}).get('song', {}).get('itemlist', None)
        if not item_list:
            return None
        mid = item_list[0].get('mid', None)
        if not mid:
            return None
        lyric_result = self.api_lyric(mid)
        lyric = lyric_result.get('lyric', None)
        if not lyric:
            return None
        return base64.b64decode(lyric).decode('utf-8')

    def fetch_cover(self, name: str, artist: str = '', album: str = '') -> Optional[str]:
        result = self.api_search_song(name, artist, album)
        item_list = result.get('data', {}).get('album', {}).get('itemlist', None)
        if not item_list:
            return None
        return item_list[0].get('pic', None)

    def api_search_song(self, name: str, artist: str = '', album: str = ''):
        key = quote_plus(f'{name} {artist}'.strip())
        url = 'https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?format=json' \
              '&inCharset=utf-8&outCharset=utf-8&key=' + key
        return requests.get(url, headers={'Referer': 'https://c.y.qq.com/'}).json()

    def api_lyric(self, mid: str):
        current_millis = int((time.time()) * 1000)
        data = {
            'pcachetime': str(current_millis),
            'songmid': mid,
            'g_tk': '5381',
            'loginUin': '0',
            'hostUin': '0',
            'format': 'json',
            'inCharset': 'utf8',
            'outCharset': 'utf8',
            'notice': '0',
            'platform': 'yqq',
            'needNewCode': '0',
        }

        url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        headers = {
                'Referer': 'https://c.y.qq.com/'
        }
        return requests.post(url, data=data, headers=headers).json()
