import json
import os.path
import queue
import shutil
import time
from typing import Any

from core.utils import PostGui
from core.webengine import BrowserBuffer
from PyQt6.QtCore import QThread, pyqtSignal

from music_service import music_service, utils
from music_service.netease import NeteaseMusicApi

logger = utils.get_logger('NeteaseBackend')


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
        self._cache_queue = queue.Queue()

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
        self._thread_post(self._start_cache_mp3_task)

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
        db_file = utils.get_db_cache_file(f'{self._api.user_id}.json')
        if os.path.isfile(db_file):
            with open(db_file, 'r') as fp:
                data = fp.read()
            songs = json.loads(data)
            self._track_infos = {x['id']: x for x in songs }
            self._exec_js('cloudUpdateTrackInfos', songs)
            logger.debug(f'load songs from cache: {os.path.basename(db_file)}')

        self._refresh_like_songs()
        logger.debug('start fetch songs from cloud')

    def _save_like_songs(self, songs):
        data = json.dumps(songs)
        with open(utils.get_db_cache_file(f'{self._api.user_id}.json'), 'w') as fp:
            fp.write(data)

    def _refresh_like_songs(self):
        self._js_post(self._api.get_like_songs, 'cloudUpdateTrackInfos', self._handle_like_songs)

    def _handle_like_songs(self, songs, _):
        self._save_like_songs(songs)
        self._track_infos = {x['id']: x for x in songs }
        return songs

    def get_track_info(self, song_id):
        song_id = int(song_id)
        return self._track_infos[song_id]

    def fetch_track_audio_source(self, song_id, track_unikey):
        logger.debug(f'fetch track audio source, song_id: {song_id}')
        song_id = int(song_id)

        info = self.get_track_info(song_id)
        mp3_name = f"{info['artist']}_{info['name']}.mp3"
        cache_mp3_file = utils.get_music_cache_file(mp3_name)
        if os.path.exists(cache_mp3_file):
            self._exec_js('cloudUpdateTrackAudioSource', cache_mp3_file)
        else:
            self._cache_quality_mp3(song_id, mp3_name)
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
            try:
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
            except Exception as e:
                logger.exception(f'login qr check error, {e}')
            time.sleep(1.0)

    def _cache_quality_mp3(self, song_id: int, mp3_name: str):
        self._cache_queue.put((song_id, mp3_name))

    def _start_cache_mp3_task(self):
        while True:
            task = self._cache_queue.get()
            if task:
                try:
                    song_id, mp3_name = task
                    url = self._api.get_exhigh_song_url(song_id)
                    temp_file = utils.get_temp_cache_file(mp3_name)
                    if utils.download_file(url, temp_file):
                        mp3_file = utils.get_music_cache_file(mp3_name)
                        shutil.move(temp_file, mp3_file)
                except Exception as e:
                    logger.exception(f'cache mp3 task, failed: {e}')
            time.sleep(2)
