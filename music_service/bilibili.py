import requests
from typing import Optional
from music_service.utils import get_logger

logger = get_logger('bilibili')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Referer': 'https://www.bilibili.com'
}

def get_song_url(name: str, artist: str) -> Optional[str]:
    try:
        keyword = f'{name} {artist}'
        song_id = api_search_song_id(keyword)
        if not song_id:
            return None
        return api_get_song_url(song_id)
    except Exception as e:
        logger.exception(f'get song url error: {e}')
        return None


def api_search_song_id(keyword: str) -> int:
    url = 'https://api.bilibili.com/audio/music-service-c/s'
    params = {
        'search_type': 'music',
        'page': 1,
        'pagesize': 30,
        'keyword': keyword
    }
    resp = requests.get(url, params=params, headers=headers).json()
    results = resp.get('data', {}).get('result', None)
    if results:
        return results[0].get('id', 0)
    return None

def api_get_song_url(song_id: int) -> Optional[str]:
    url = 'https://www.bilibili.com/audio/music-service-c/web/url'
    params = {
        'rivilege': "2",
        'quality': "2",
        'sid': song_id
    }
    resp = requests.get(url, params=params, headers=headers)
    return resp.json().get('data', {}).get('cdns', [None])[0]
