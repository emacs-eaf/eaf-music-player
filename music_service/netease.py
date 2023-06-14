import json
import random
import rsa
import rsa.core
import rsa.common
import rsa.transform
import requests

from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from typing import Optional
from music_service.base import BaseProvider


IV = b'0102030405060708'
PRESET_KEY = b'0CoJUm6Qyw8W8jud'
PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ37BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV8k4cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44oncaTWz7OBGLbCiK45wIDAQAB
-----END PUBLIC KEY-----'''
BASE64 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


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


def weapi_request(url, data: dict, encrypted: bool = True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/13.10586',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://music.163.com',
        'Cookie': '__remember_me=true; NMTID=87c5691ddbb8ad34dee6980781bb0d09; _'
                  'ntes_nuid=ae70727d77e51f03a4a11c026fcc2fe3; '
                  'MUSIC_A=bf8bfeabb1aa84f9c8c3906c04a04fb864322804c83f5d607e91a04eae463c943'
                  '6bd1a17ec353cf780b396507a3f7464e8a60f4bbc019437993166e004087dd32d1490298ca'
                  'f655c2353e58daa0bc13cc7d5c198250968580b12c1b8817e3f5c807e650dd04abd3fb8130b7ae43fcc5b'
    }
    if encrypted:
        data = weapi_encrypt(data)
    return requests.post(url, data=data, headers=headers).json()


def search_song(keyword: str):
    url = 'https://music.163.com/weapi/search/get'
    data = {
        's': keyword,
        'type': 1,
        'limit': 10,
        'offset': 0,
        'csrf_token': ""
    }
    return weapi_request(url, data)


def download_lyric(song_id: int):
    url = 'https://music.163.com/api/song/lyric?_nmclfl=1'
    data = {
        'id': song_id,
        'tv': -1,
        'lv': -1,
        'rv': -1,
        'kv': -1
    }
    return weapi_request(url, data, encrypted=False)


class NeteaseMusicApi(BaseProvider):
    provider_name = "netease"

    def lyric(self, name: str, artist: str = "", album: str = "") -> Optional[str]:
        keywords = f"{name} {artist} {album}".strip()
        search_result = search_song(keywords)
        songs = search_result.get("result", {}).get("songs", None)
        if not songs:
            return None
        song_id = songs[0].get("id", 0)
        if not song_id:
            return None
        lyric_result = download_lyric(song_id)
        return lyric_result.get("lrc", {}).get("lyric", None)
