import shutil
from music_service.service import music_service

try:
    import rsa
    from Crypto.Cipher import AES
except ImportError:
    print("[MusicService] netease require pycryptodome and rsa module, " \
          "use `pip install pycryptodome rsa` to install")
else:
    from music_service.netease import NeteaseMusicApi
    music_service.register_provider(NeteaseMusicApi())

from music_service.qq import QQMusicApi
music_service.register_provider(QQMusicApi())

if shutil.which('album-art'):
    from music_service.album_art import AlbumArt
    music_service.register_provider(AlbumArt())
else:
    print('[MusicService] Please run `sudo npm i -g album-art` package to fetch cover')
