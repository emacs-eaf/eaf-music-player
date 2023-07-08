import html
import os.path
import re
import json
import base64
from collections import OrderedDict
from typing import Dict, Optional

from PIL import Image

from music_service.base import BaseProvider, BaseSongProvider
from music_service.utils import download_file, get_logger

try:
    from music_service import bridge_server
except ImportError:
    bridge_server = None


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
    _song_prividers: Dict[str, BaseSongProvider]
    has_proprietary_codecs: bool = False

    def __init__(self):
        self._prividers = OrderedDict()
        self._song_prividers = OrderedDict()
        self._bridge_server_port = 0

    def run_bridge_server(self, port: int):
        if bridge_server:
            bridge_server.run_server_multiprocess(port)
            self._bridge_server_port = port

    def _get_bridge_song_url(self, url: str, request_headers: dict) -> Optional[str]:
        if not url:
            return None
        if not self._bridge_server_port:
            return None

        if request_headers:
            headers = base64.b64encode(json.dumps(request_headers).encode('utf-8')).decode('utf-8')
        else:
            headers = ''
        url = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        return f'http://127.0.0.1:{self._bridge_server_port}/forward?url={url}&headers={headers}'

    def register_provider(self, provider: BaseProvider):
        self._prividers[provider.provider_name] = provider

    def register_song_provider(self, provider: BaseSongProvider):
        self._song_prividers[provider.provider_name] = provider

    def remove_provider(self, name: str):
        if name in self._prividers:
            del self._prividers[name]

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        return self._prividers.get(name, None)

    def fetch_lyric(self, name: str, artist: str = '', album: str = '', song_id: int = 0) -> Optional[str]:
        name = refine(name)
        artist = refine(artist)
        album = refine(album)
        for provider in self._prividers.values():
            try:
                log.debug(f'fetch lyric provider: {provider.provider_name} name: {name}, ' \
                          f'artist: {artist}, album: {album}')
                result = provider.fetch_lyric(name, artist, album, song_id)
                if result and check_lyric_is_valid(result):
                    return html.unescape(refine_lyrics(result))
            except Exception as e:
                log.exception(f'provider: {provider.provider_name} fetch lyric error: {e}')
                continue
        return None


    def fetch_cover(self, save_path: str, name: str, artist: str = '', album: str = '', song_id: int = 0) -> bool:
        name = refine(name)
        artist = refine(artist)
        album = refine(album)
        for provider in self._prividers.values():
            try:
                cover_url = provider.fetch_cover(name, artist, album, song_id)
                log.debug(f'fetch cover provider: {provider.provider_name} ' \
                          f'name: {name}, cover_url: {cover_url}')
                if cover_url and download_file(cover_url, save_path):
                    if check_cover_is_valid(save_path):
                        return True
            except Exception as e:
                log.exception(f'provider: {provider.provider_name} fetch cover error: {e}')
                continue
        return False

    def fetch_song_url(self, name: str, artist: str = '', album: str = '') -> Optional[str]:
        name = refine(name)
        artist = refine(artist)
        album = refine(album)
        for provider in self._song_prividers.values():
            if provider.use_proprietary_codecs and not self.has_proprietary_codecs:
                continue

            if provider.require_bridge and self._bridge_server_port == 0:
                continue

            url = provider.fetch_song_url(name, artist, album)
            if not url:
                continue

            if provider.require_bridge:
                url = self._get_bridge_song_url(url, provider.get_bridge_http_headers())
            return url

music_service = MusicService()
