import re
from music_service.base import BaseProvider
from typing import Dict, Optional
from collections import OrderedDict


def refine(s: str) -> str:
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[\(\)\[\]\/!?@#￥%…&*・]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


class MusicService:
    _prividers: Dict[str, BaseProvider]

    def __init__(self):
        self._prividers = OrderedDict()

    def register_provider(self, provider: BaseProvider):
        self._prividers[provider.provider_name] = provider

    def remove_provider(self, name: str):
        if name in self._prividers:
            del self._prividers[name]

    def lyric(self, name: str, artist: str = "", album: str = "") -> Optional[str]:
        name = refine(name)
        artist = refine(artist)
        album = refine(album)
        for provider in self._prividers.values():
            try:
                print(f"[MusicService] provider: {provider.provider_name} name: {name}, " \
                      f"artist: {artist}, album: {album}")
                result = provider.lyric(name, artist, album)
                if result:
                    return result
            except Exception as e:
                print(f"[MusicService] provider: {provider.provider_name} lyric error: {e}")
                continue
        return None


music_service = MusicService()
