import requests
from typing import Optional
from music_service.utils import USER_AGENT
from music_service.base import BaseSongProvider

headers = {
    'User-Agent': USER_AGENT,
    'Referer': 'https://www.bilibili.com'
}


class Bilibili(BaseSongProvider):
    provider_name = 'bilibili'
    require_bridge = True
    use_proprietary_codecs = True

    def fetch_song_url(self, name: str, artist: str = '', album: str = ''):
        keyword = f'{name} {artist}'
        song_id = self.api_search_song_id(keyword)
        if not song_id:
            return None
        return self.api_get_song_url(song_id)

    def get_bridge_http_headers(self) -> dict:
        return {
            'Referer': headers['Referer']
        }

    def api_search_song_id(self, keyword: str) -> int:
        url = 'https://api.bilibili.com/audio/music-service-c/s'
        params = {
            'search_type': 'music',
            'page': 1,
            'pagesize': 30,
            'keyword': keyword
        }
        resp = requests.get(url, params=params, headers=headers, timeout=5.0).json()
        results = resp.get('data', {}).get('result', None)
        if results:
            return results[0].get('id', 0)
        return None

    def api_get_song_url(self, song_id: int) -> Optional[str]:
        url = 'https://www.bilibili.com/audio/music-service-c/web/url'
        params = {
            'rivilege': "2",
            'quality': "2",
            'sid': song_id
        }
        resp = requests.get(url, params=params, headers=headers, timeout=5.0)
        return resp.json().get('data', {}).get('cdns', [None])[0]
