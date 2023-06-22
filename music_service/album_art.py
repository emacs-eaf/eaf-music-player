import subprocess
from typing import Optional

from music_service.base import BaseProvider


class AlbumArt(BaseProvider):
    provider_name = 'album-art'

    def fetch_lyric(self, name: str, artist: str = '', album: str = '', song_id: int = 0) -> Optional[str]:
        pass

    def fetch_cover(self, name: str, artist: str = '', album: str = '', song_id: int = 0) -> Optional[str]:
        if artist:
            fake_album = album if album else name
            cmd = f"album-art '{artist}' '{fake_album}'"
        else:
            fake_album = album if album else name
            cmd = f"album-art '{fake_album}'"
        return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
