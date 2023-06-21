import hashlib
import json
import os.path
import random
from base64 import b64encode
from enum import Enum
from typing import List, Optional, Union

import requests
import requests.utils
import rsa
import rsa.common
import rsa.core
import rsa.transform
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

from music_service.base import BaseProvider
from music_service.utils import USER_AGENT, get_cookie_cache_file, get_logger

logger = get_logger('NeteaseMusicApi')


IV = b'0102030405060708'
PRESET_KEY = b'0CoJUm6Qyw8W8jud'
EAPI_KEY = b'e82ckenh8dichen8'
PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ37BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV8k4cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44oncaTWz7OBGLbCiK45wIDAQAB
-----END PUBLIC KEY-----'''
BASE64 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


HTTP_DEFAULT_COOKIES = '__remember_me=true; NMTID=87c5691ddbb8ad34dee6980781bb0d09; _ntes_nuid=ae70727d77e51f03a4a11c026fcc2fe3; MUSIC_A=bf8bfeabb1aa84f9c8c3906c04a04fb864322804c83f5d607e91a04eae463c9436bd1a17ec353cf780b396507a3f7464e8a60f4bbc019437993166e004087dd32d1490298caf655c2353e58daa0bc13cc7d5c198250968580b12c1b8817e3f5c807e650dd04abd3fb8130b7ae43fcc5b'


def rsa_encrypt(buffer: bytes, key: str) -> bytes:
    pubkey = RSA.import_key(key)
    key_len = rsa.common.byte_size(pubkey.n)
    buffer = bytes(key_len - len(buffer)) + buffer
    _b = rsa.transform.bytes2int(buffer)
    _i = rsa.core.encrypt_int(_b, pubkey.e, pubkey.n)
    result = rsa.transform.int2bytes(_i, key_len)
    return result

def aes_cbc_encrypt(buffer: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(buffer, AES.block_size))

def aes_ecb_encrypt(buffer: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(buffer, AES.block_size))

def aes_ecb_decrypt(buffer: bytes, key: bytes) -> bytes:
    decipher = AES.new(key, AES.MODE_ECB)
    return unpad(decipher.decrypt(buffer), AES.block_size)

def weapi_encrypt(req_data: dict):
    text = json.dumps(req_data).encode('utf-8')
    secret_key = bytes([random.choice(BASE64).encode('utf-8')[0] for _ in range(16)])

    params = b64encode(aes_cbc_encrypt(b64encode(aes_cbc_encrypt(text, PRESET_KEY, IV)), secret_key, IV))
    enc_sec_key = rsa_encrypt(secret_key[::-1], PUBLIC_KEY)
    return {
        'params': params.decode('utf-8'),
        'encSecKey': enc_sec_key.hex()
    }

def eapi_encrypt(url, req_data):
    text = json.dumps(req_data)
    message = f'nobody{url}use{text}md5forencrypt'
    md5 = hashlib.md5(message.encode('utf-8')).hexdigest()
    data = f'{url}-36cd479b6b5-{text}-36cd479b6b5-{md5}'
    params = aes_ecb_encrypt(data.encode('utf-8'), EAPI_KEY).hex().upper()
    return {
        'params': params
    }

def eapi_decrypt(resp_buffer: bytes):
    return aes_ecb_decrypt(resp_buffer, EAPI_KEY)


class ApiCrypto(Enum):
    Unknown = 0
    Api = 1
    WeApi = 2
    EApi = 3


class NeteaseMusicApi(BaseProvider):
    provider_name = 'netease'

    def __init__(self):
        super().__init__()
        self._session = requests.session()
        self._session.headers['User-Agent'] = USER_AGENT
        self._session.headers['Referer'] = 'https://music.163.com'
        # self._session.headers['X-Real-IP'] = '27.18.2.122'
        # self._session.headers['X-Forwarded-For'] = '27.18.2.122'

        # load cookies
        self._unikey = ''
        self._load_cookies()
        self.user_id = 0

    def _load_default_cookies(self):
        kvs = [kv for kv in HTTP_DEFAULT_COOKIES.split('; ')]
        cookies = {}
        for kv in kvs:
            k, v = kv.split('=')
            cookies[k] = v
        self._session.cookies = requests.utils.cookiejar_from_dict(cookies)

    def _load_cookies_from_file(self, file_path: str):
        with open(file_path, 'r') as fp:
            data = fp.read()
        cookies = json.loads(data)
        self._session.cookies = requests.utils.cookiejar_from_dict(cookies)

    def _load_cookies(self):
        cookie_file = get_cookie_cache_file('netease.json')
        if os.path.exists(cookie_file):
            logger.debug(f'load cookies from file: {cookie_file}')
            self._load_cookies_from_file(cookie_file)
        else:
            logger.debug('load default cookies')
            self._load_default_cookies()

    def _save_cookies(self):
        cookie_file = get_cookie_cache_file('netease.json')
        cookies = requests.utils.dict_from_cookiejar(self._session.cookies)
        with open(cookie_file, 'w') as fp:
            fp.write(json.dumps(cookies))

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
        url = songs[0].get('al', {}).get('picUrl', None)
        if url:
            return f'{url}?param=200y200'
        return None

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

    def _post(self, url: str, data=None, crypto: ApiCrypto = ApiCrypto.Unknown, options=None):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if not options:
            options = {}
        if not data:
            data = {}
        if crypto == ApiCrypto.WeApi:
            data['csrf_token'] = self._session.cookies.get('__csrf', '')
            data = weapi_encrypt(data)
        elif crypto == ApiCrypto.EApi:
            data = eapi_encrypt(options.get('url', ''), data)
            resp_data = self._session.post(url, data=data, headers=headers).content
            try:
                return json.loads(eapi_decrypt(resp_data))
            except Exception:
                return json.loads(resp_data)
        return self._session.post(url, data=data, headers=headers).json()

    def is_login(self) -> bool:
        self.user_id = self.get_user_id()
        return bool(self.user_id)

    def get_user_id(self) -> int:
        resp = self.api_user_account()
        account = resp.get('account', None)
        if not account:
            return 0
        status = account.get('status', -1)
        if status != 0:
            return 0
        return account.get('id', 0)

    def login_qr_create(self):
        qr_result = self.api_login_qr_key()
        self._unikey = qr_result.get('unikey', '')
        if not self._unikey:
            qrcode = ''
        else:
            qrcode = self.api_login_qr_create(self._unikey)
        return {
            'qrcode': qrcode
        }

    def login_qr_check(self):
        return self.api_login_qr_check(self._unikey)

    def get_like_songs(self) -> Optional[List]:
        uid = self.get_user_id()
        self.user_id = uid
        if not uid:
            logger.error('not login')
            return None
        playlist_resp = self.api_user_playlist(uid)
        playlist = playlist_resp.get('playlist', None)
        if not playlist:
            logger.error('get playlist failed or playlist is empty')
            return None
        pid = playlist[0].get('id', 0)
        pname = playlist[0].get('name', '')
        if not pid:
            logger.error('playlist id error')
            return None
        detail_resp = self.api_playlist_detail(pid)
        track_id_infos = detail_resp['playlist']['trackIds']
        song_ids = [track['id'] for track in track_id_infos]
        song_detail_resp = self.api_song_detail(song_ids)
        songs = song_detail_resp.get('songs', None)
        if not songs:
            logger.error(f'the like playlist: {pname} get songs failed')
            return None

        song_list = []
        for song in songs:
            song_info = {
                'id': song['id'],
                'name': song['name'],
                'artist': song.get('ar', [{}])[0].get('name', ''),
                'album': song.get('al', {}).get('name', ''),
                'album_url': song.get('al', {}).get('picUrl', '')
            }
            song_list.append(song_info)
        return song_list

    def get_song_url(self, song_id: int):
        result = self.api_song_url_v1(song_id)
        url = result['data'][0].get('url', '')
        return {
            'id': song_id,
            'url': url
        }

    def get_exhigh_song_url(self, song_id: int) -> str:
        result = self.api_song_url_v1(song_id, 'exhigh')
        url = result['data'][0].get('url', '')
        return url

    def api_login_qr_key(self):
        url = 'https://music.163.com/weapi/login/qrcode/unikey'
        data = {
            'type': 1
        }
        return self._post(url, data, crypto=ApiCrypto.WeApi)

    def api_login_qr_create(self, key: str) -> str:
        return f'https://music.163.com/login?codekey={key}'

    def api_login_qr_check(self, key: str):
        '''
        轮询此接口可获取二维码扫码状态
        800 为二维码过期
        801 为等待扫码
        802 为待确认
        803 为授权登录成功(803 状态码下会返回 cookies)
        '''
        url = 'https://music.163.com/weapi/login/qrcode/client/login'
        data = {
            'key': key,
            'type': 1
        }
        resp = self._post(url, data, crypto=ApiCrypto.WeApi)
        if resp.get('code', 0) == 803:
            logger.info('scan qrcode login success, start save cookies')
            self._save_cookies()
        return resp

    def api_user_account(self):
        url = 'https://music.163.com/api/nuser/account/get'
        data = {}
        return self._post(url, data, crypto=ApiCrypto.WeApi)

    def api_user_playlist(self, uid: int, limit: int = 30, offset: int = 0):
        url = 'https://music.163.com/weapi/user/playlist'
        data = {
            'uid': uid,
            'limit': limit,
            'offset': offset,
            'includeVideo': True
        }
        return self._post(url, data, crypto=ApiCrypto.WeApi)

    def api_playlist_detail(self, pid: int, s: int = 8):
        url = 'https://music.163.com/api/v6/playlist/detail'
        data = {
            'id': pid,
            'n': 100000,
            's': s
        }
        return self._post(url, data, crypto=ApiCrypto.Api)

    def api_song_url(self, song_id: Union[List[int],int], br: int = 999000):
        if isinstance(song_id, int):
            song_id = [song_id]
        data = {
            'ids': json.dumps(song_id),
            'br': br
        }
        url = 'https://interface3.music.163.com/eapi/song/enhance/player/url'
        options = {
            'url': '/api/song/enhance/player/url'
        }
        return self._post(url, data, crypto=ApiCrypto.EApi, options=options)

    def api_song_url_v1(self, song_id: Union[List[int],int], level: str = 'standard'):
        '''
        level: standard, exhigh, lossless, hires
        '''
        if isinstance(song_id, int):
            song_id = [song_id]
        data = {
            'ids': json.dumps(song_id),
            'level': level,
            'encodeType': 'flac'
        }
        url = 'https://interface.music.163.com/eapi/song/enhance/player/url/v1'
        options = {
            'url': '/api/song/enhance/player/url/v1'
        }
        return self._post(url, data, crypto=ApiCrypto.EApi, options=options)

    def api_song_download_url(self, song_id: int, br: int = 999000):
        data = {
            'id': song_id,
            'br': br
        }
        url = 'https://interface.music.163.com/eapi/song/enhance/download/url'
        options = {
            'url': '/api/song/enhance/download/url'
        }
        return self._post(url, data, crypto=ApiCrypto.EApi, options=options)

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
