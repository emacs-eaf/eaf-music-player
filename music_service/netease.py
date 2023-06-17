from ctypes import Union
import json
import random
from requests.utils import default_headers
import rsa
import rsa.core
import rsa.common
import rsa.transform
import requests
from enum import Enum

from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from typing import Optional, Union, List
from music_service.base import BaseProvider


IV = b'0102030405060708'
PRESET_KEY = b'0CoJUm6Qyw8W8jud'
PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ37BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV8k4cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44oncaTWz7OBGLbCiK45wIDAQAB
-----END PUBLIC KEY-----'''
BASE64 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

HTTP_DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/13.10586',
    'Referer': 'https://music.163.com',
    'Cookie': '__remember_me=true; NMTID=87c5691ddbb8ad34dee6980781bb0d09; _'
              'ntes_nuid=ae70727d77e51f03a4a11c026fcc2fe3; '
              'MUSIC_A=bf8bfeabb1aa84f9c8c3906c04a04fb864322804c83f5d607e91a04eae463c943'
              '6bd1a17ec353cf780b396507a3f7464e8a60f4bbc019437993166e004087dd32d1490298ca'
              'f655c2353e58daa0bc13cc7d5c198250968580b12c1b8817e3f5c807e650dd04abd3fb8130b7ae43fcc5b'
}


def rsa_encrypt(buffer: bytes, key: str) -> bytes:
    pubkey = RSA.import_key(key)
    key_len = rsa.common.byte_size(pubkey.n)
    buffer = bytes(key_len - len(buffer)) + buffer
    _b = rsa.transform.bytes2int(buffer)
    _i = rsa.core.encrypt_int(_b, pubkey.e, pubkey.n)
    result = rsa.transform.int2bytes(_i, key_len)
    return result


def aes_encrypt(buffer: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(buffer, AES.block_size))


def weapi_encrypt(req_data: dict):
    text = json.dumps(req_data).encode('utf-8')
    secret_key = bytes([random.choice(BASE64).encode('utf-8')[0] for _ in range(16)])

    params = b64encode(aes_encrypt(b64encode(aes_encrypt(text, PRESET_KEY, IV)), secret_key, IV))
    enc_sec_key = rsa_encrypt(secret_key[::-1], PUBLIC_KEY)
    return {
        'params': params.decode('utf-8'),
        'encSecKey': enc_sec_key.hex()
    }


class ApiCrypto(Enum):
    Unknown = 0
    Api = 1
    WeApi = 2


class NeteaseMusicApi(BaseProvider):
    provider_name = 'netease'

    def __init__(self):
        super().__init__()

        self._session = requests.session()

    def fetch_lyric(self, name: str, artist: str = '', album: str = '') -> Optional[str]:
        song_id = self.get_song_id(name, artist, album, fuzzy=False)
        if not song_id:
            return None
        lyric_result = self.api_lyric(song_id)
        return lyric_result.get('lrc', {}).get('lyric', None)

    def fetch_cover(self, name: str, artist: str = '', album: str = '') -> Optional[str]:
        song_id = self.get_song_id(name, artist, album, fuzzy=False)
        if not song_id:
            return None
        result = self.api_song_detail(song_id)
        songs = result.get('songs', None)
        if not songs:
            return None
        return songs[0].get('al', {}).get('picUrl', None)

    def get_song_id(self, name: str, artist: str = '', album: str = '', fuzzy: bool = True) -> Optional[int]:
        keywords = f'{name} {artist}'.strip()
        search_result = self.api_search_song(keywords)
        songs = search_result.get('result', {}).get('songs', None)
        if not songs:
            return None
        song_id = 0
        for song in songs:
            song_name = song.get('name', '')
            artist = artist.strip()
            if artist:
                song_artists = [item.get('name', '') for item in song.get('artists', [])]
                if song_name == name and any([x in artist for x in song_artists]):
                    song_id = song.get('id', 0)
                    break
            else:
                if song_name == name:
                    song_id = song.get('id', 0)
                    break

        if not song_id and fuzzy:
            song_id = songs[0].get('id', 0)
        return song_id

    def _post(self, url: str, data=None, crypto: ApiCrypto = ApiCrypto.Unknown):
        headers = HTTP_DEFAULT_HEADERS.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        if not data:
            data = {}
        if crypto == ApiCrypto.WeApi:
            data['csrf_token'] = ''
            data = weapi_encrypt(data)
        return self._session.post(url, data=data, headers=headers).json()


    def api_search_song(self, keyword: str, search_type: int = 1, limit: int = 10, offset: int = 0):
        url = 'https://music.163.com/weapi/search/get'
        data = {
            's': keyword,
            'type': search_type,
            'limit': limit,
            'offset': offset
        }
        return self._post(url, data, crypto=ApiCrypto.WeApi)

    def api_lyric(self, song_id: int):
        url = 'https://music.163.com/api/song/lyric?_nmclfl=1'
        data = {
            'id': song_id,
            'tv': -1,
            'lv': -1,
            'rv': -1,
            'kv': -1
        }
        return self._post(url, data, crypto=ApiCrypto.Api)

    def api_song_detail(self, song_id: Union[List[int], int]):
        url = 'https://music.163.com/weapi/v3/song/detail'
        if isinstance(song_id, int):
            song_id = [song_id]
        song_id_infos = [{'id': sid} for sid in song_id]
        data = {
            'c': json.dumps(song_id_infos)
        }
        return self._post(url, data, crypto=ApiCrypto.WeApi)
