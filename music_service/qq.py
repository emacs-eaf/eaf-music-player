import time
import base64
import requests
from urllib.parse import quote_plus
from typing import Optional
from music_service.base import BaseProvider

class QQMusicApi(BaseProvider):
    provider_name = "qq"


    def lyric(self, name: str, artist: str = "", album: str = "") -> Optional[str]:
        mid = self._search_song(name, artist, album)
        if not mid:
            return None
        return self._download_lyric(mid)

    def _search_song(self, name: str, artist: str = "", album: str = "") -> Optional[str]:
        key = quote_plus(f"{name} {artist}".strip())
        url = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?format=json" \
              "&inCharset=utf-8&outCharset=utf-8&key=" + key
        try:
            result = requests.get(url, headers={"Referer": "https://c.y.qq.com/"}).json()
        except Exception as e:
            print(f"query name: {name}, artist: {artist} lyric fail: {e}")
            result = {}
        item_list = result.get("data", {}).get("song", {}).get("itemlist", None)
        if not item_list:
            return None
        return item_list[0].get("mid", None)

    def _download_lyric(self, mid: str) -> Optional[str]:
        if not mid:
            return None
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
        try:
            result = requests.post(url, data=data, headers=headers).json()
        except Exception as e:
            print(f"[qqmusic lyric] download mid: {mid} fail: {e}")
            result = {}

        lyric = result.get("lyric", None)
        if not lyric:
            return None
        return base64.b64decode(lyric).decode("utf-8")
