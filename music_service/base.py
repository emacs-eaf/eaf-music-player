from typing import Optional


class BaseProvider:
    provider_name: str = ""

    def lyric(self, name: str, artist: str = "", album: str = "") -> Optional[str]:
        raise NotImplementedError()
