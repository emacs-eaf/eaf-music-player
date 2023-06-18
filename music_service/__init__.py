from music_service.album_art import AlbumArt
from music_service.netease import NeteaseMusicApi
from music_service.qq import QQMusicApi
from music_service.service import music_service

music_service.register_provider(AlbumArt())
music_service.register_provider(NeteaseMusicApi())
music_service.register_provider(QQMusicApi())
