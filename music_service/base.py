from typing import Optional


class BaseProvider:
    provider_name: str = ''

    def fetch_lyric(self, name: str, artist: str = '', album: str = '', song_id: int = 0) -> Optional[str]:
        raise NotImplementedError()

    def fetch_cover(self, name: str, artist: str = '', album: str = '', song_id: int = 0) -> Optional[str]:
        raise NotImplementedError()


class BaseSongProvider:
    provider_name: str = ''
    require_bridge: bool = False
    use_proprietary_codecs: bool = False

    def fetch_song_url(self, name: str, artist: str = '', album: str = ''):
        raise NotImplementedError()

    def get_bridge_http_headers(self) -> dict:
        return {}
