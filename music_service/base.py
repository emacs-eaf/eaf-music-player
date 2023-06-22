from typing import Optional


class BaseProvider:
    provider_name: str = ""

    def fetch_lyric(self, name: str, artist: str = "", album: str = "", song_id: int = 0) -> Optional[str]:
        raise NotImplementedError()

    def fetch_cover(self, name: str, artist: str = "", album: str = "", song_id: int = 0) -> Optional[str]:
        raise NotImplementedError()
