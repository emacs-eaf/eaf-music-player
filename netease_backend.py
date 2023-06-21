import time
from typing import Any

from core.utils import PostGui
from core.webengine import BrowserBuffer
from PyQt6.QtCore import QThread, pyqtSignal

from music_service import music_service
from music_service.netease import NeteaseMusicApi
from music_service.utils import get_logger

logger = get_logger('NeteaseBackend')


class SafeThread(QThread):
    _notify_signal = pyqtSignal(object)

    def __init__(self, exec_func, handle_func=None, handle_arg=None, *args, **kwargs):
        super().__init__()
        self._notify_signal.connect(self._do_notify)
        self._exec_func = exec_func
        self._handle_func = handle_func
        self._handle_arg = handle_arg
        self._exec_args = args
        self._exec_kwargs = kwargs

    def run(self):
        try:
            result = self._exec_func(*self._exec_args, **self._exec_kwargs)
        except Exception as e:
            logger.exception(f'SafeThread exec func: {self._exec_func.__name__}, failed: {e}')
            result = None
        self._notify_signal.emit(result)

    def _do_notify(self, result: Any):
        if not self._handle_func:
            return
        try:
            self._handle_func(result, self._handle_arg)
        except Exception as e:
            logger.exception(f'SafeThread handle func: {self._handle_func.__name__}, failed: {e}')


class NeteaseBackend:

    def __init__(self, buffer: BrowserBuffer):
        self._buffer = buffer
        self._api: NeteaseMusicApi = music_service.get_provider('netease')
        self._thread_caches = []
        self._track_infos = {}

    def _thread_post(self, exec_func, handle_func=None, handle_arg=None, *args, **kwargs):
        task = SafeThread(exec_func, handle_func, handle_arg, *args, **kwargs)
        self._thread_caches.append(task)
        task.start()

    def _js_post(self, exec_func, js_method: str, handle_func=None, handle_arg=None, *args, **kwargs):
        self._thread_post(exec_func, self._eval_js_handle(js_method, handle_func), handle_arg, *args, **kwargs)

    def _eval_js_handle(self, js_method: str, handle_func=None):
        def wrapper(result: Any, handle_arg: Any):
            if handle_func:
                result = handle_func(result, handle_arg)
            self._buffer.buffer_widget.eval_js_function(js_method, result)
        return wrapper

    def _exec_js(self, js_method, val):
        self._buffer.buffer_widget.eval_js_function(js_method, val)

    @PostGui()
    def _post_exec_js(self, js_method, val):
        self._exec_js(js_method, val)

    def init_app(self):
        self._thread_post(self._api.is_login, self._handle_user_login)

    def _handle_user_login(self, is_login, _):
        self._exec_js('cloudUpdateLoginState', is_login)

        logger.debug(f'login state: {is_login}')
        if is_login:
            logger.debug('is logined, start load like songs')
            self._load_like_songs()
        else:
            logger.debug('is not login, start get login qrcode')
            self._login_qr_create()

    def _load_like_songs(self):
        # todo load cache
        self._refresh_like_songs()

    def _refresh_like_songs(self):
        self._js_post(self._api.get_like_songs, 'cloudUpdateTrackInfos', self._handle_like_songs)

    def _handle_like_songs(self, songs, _):
        self._track_infos = {x['id']: x for x in songs }
        return songs

    def get_track_info(self, song_id):
        song_id = int(song_id)
        return self._track_infos[song_id]

    def fetch_track_audio_source(self, song_id, track_unikey):
        logger.debug(f'fetch track audio source, song_id: {song_id}')
        song_id = int(song_id)
        self._thread_post(self._api.get_song_url, self._handle_fetch_audio_source, track_unikey, song_id)

    def _handle_fetch_audio_source(self, info, track_unikey):
        url = ''
        if info:
            url = info['url']
        if self._buffer.is_current_play_track(track_unikey):
            logger.debug(f'cloudUpdateTrackAudioSource url: {url}')
            self._exec_js('cloudUpdateTrackAudioSource', url)
        else:
            logger.debug('is not current track, ignore')

    def _login_qr_create(self):
        self._js_post(self._api.login_qr_create, 'cloudUpdateLoginQr')

        logger.info('start login qrcode check task')
        self._thread_post(self._loop_check_qrcode)

    @PostGui()
    def _do_login_success(self):
        logger.info('notify user login success')
        self._exec_js('cloudUpdateLoginState', True)

        logger.info('get like songs')
        self._refresh_like_songs()

    def _loop_check_qrcode(self):
        while True:
            result = self._api.login_qr_check()
            code = result.get('code')

            # expired
            if code == 800:
                qrcode = self._api.login_qr_create()
                logger.debug(f'loign qrcode is expired, renew: {qrcode}')
                self._post_exec_js('cloudUpdateLoginQr', qrcode)
            elif code == 803:
                logger.debug('login qrcode success')
                self._do_login_success()
                break
            time.sleep(1.0)
