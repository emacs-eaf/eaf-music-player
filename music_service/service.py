import html
import os.path
import re
from collections import OrderedDict
from typing import Dict, Optional

from PIL import Image

from music_service.base import BaseProvider
from music_service.utils import download_file, get_logger

lrc_pattern = re.compile(r'^\[\d{2}:\d{2}\.\d+\]')
log = get_logger('MusicService')


def refine(s: str) -> str:
    s = re.sub(r'[\(\)\[\]\/!?@#￥%…&*・]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def check_lyric_is_valid(lyric: str) -> bool:
    lines = lyric.splitlines()
    if len(lines) < 10:
        return False
    return bool(lrc_pattern.match(lines[8]))

def refine_lyrics(lyrics: str) -> str:
    return re.sub(r'\[(ti|ar|al|by|offset):.*?\](\n|\r\n)', '', lyrics)

def check_cover_is_valid(cover_path: str) -> bool:
    if not os.path.exists(cover_path):
        return False

    try:
        with Image.open(cover_path) as img:
            img.verify()
        return True
    except Exception:
        pass

    try:
        os.unlink(cover_path)
    except:
        pass
    return False


class MusicService:
    _prividers: Dict[str, BaseProvider]

    def __init__(self):
        self._prividers = OrderedDict()

    def register_provider(self, provider: BaseProvider):
        self._prividers[provider.provider_name] = provider

    def remove_provider(self, name: str):
        if name in self._prividers:
            del self._prividers[name]

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        return self._prividers.get(name, None)

    def fetch_lyric(self, name: str, artist: str = '', album: str = '') -> Optional[str]:
        name = refine(name)
        artist = refine(artist)
        album = refine(album)
        for provider in self._prividers.values():
            try:
                log.debug(f'fetch lyric provider: {provider.provider_name} name: {name}, ' \
                          f'artist: {artist}, album: {album}')
                result = provider.fetch_lyric(name, artist, album)
                if result and check_lyric_is_valid(result):
                    return html.unescape(refine_lyrics(result))
            except Exception as e:
                log.exception(f'provider: {provider.provider_name} fetch lyric error: {e}')
                continue
        return None


    def fetch_cover(self, save_path: str, name: str, artist: str = '', album: str = '') -> bool:
        name = refine(name)
        artist = refine(artist)
        album = refine(album)
        for provider in self._prividers.values():
            try:
                cover_url = provider.fetch_cover(name, artist, album)
                log.debug(f'fetch cover provider: {provider.provider_name} ' \
                          f'name: {name}, cover_url: {cover_url}')
                if cover_url and download_file(cover_url, save_path):
                    if check_cover_is_valid(save_path):
                        return True
            except Exception as e:
                log.exception(f'provider: {provider.provider_name} fetch cover error: {e}')
                continue
        return False


music_service = MusicService()
