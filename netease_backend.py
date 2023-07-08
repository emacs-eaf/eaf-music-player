import json
import os.path
import queue
import shutil
import time
from typing import Any

from core.utils import PostGui, get_emacs_var
from core.webengine import BrowserBuffer
from PyQt6.QtCore import QThread, pyqtSignal

from music_service import music_service, utils
from music_service.netease import NeteaseMusicApi
from music_service.utils import normalize_path

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

        # current tracks
        self._track_infos = {}

        # playlists
        self._like_playlist_id = 0
        self._current_playlist_id = 0
        self._user_playlists = []

        self._cache_queue = queue.Queue()
        self._logined = False

        self.music_cache_dir = get_emacs_var("eaf-music-cache-dir")
        if self.music_cache_dir == "":
            self.music_cache_dir = os.path.join(utils.get_cloud_cache_dir(), "music")
            logger.debug(f'music cache dir: {self.music_cache_dir}')

    def get_music_cache_file(self, name):
        if not os.path.exists(self.music_cache_dir):
            os.makedirs(self.music_cache_dir)

        return normalize_path(os.path.join(self.music_cache_dir, name))

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

    def init_app(self, default_playlist_id: int):
        if self._load_playlists():
            if default_playlist_id == self._like_playlist_id or default_playlist_id == 0:
                load_state = self._load_like_songs()
            else:
                load_state = self._load_playlist_songs(f'tracks_{default_playlist_id}.json')

            if load_state and default_playlist_id:
                self._current_playlist_id = default_playlist_id
        else:
            self._load_like_songs()

        self._thread_post(self._api.is_login, self._handle_user_login)
        self._thread_post(self._start_cache_mp3_task)

    def _handle_user_login(self, is_login, _):
        logger.debug(f'login state: {is_login}')
        self._exec_js('cloudUpdateLoginState', is_login)
        if is_login:
            self._logined = True
            logger.debug('is logined, start refresh playlist')
            self.refresh_playlists()
        else:
            logger.debug('is not login, start get login qrcode')
            self._login_qr_create()

    def _load_playlists(self) -> bool:
        db_file = utils.get_db_cache_file('playlists.json')
        if os.path.isfile(db_file):
            with open(db_file, 'r') as fp:
                data = fp.read()
            playlists = json.loads(data)
            self._current_playlist_id = playlists[0]['id']
            self._like_playlist_id = self._current_playlist_id
            self._user_playlists = playlists
            self._exec_js('cloudUpdatePlaylists', playlists)
            return True
        return False

    def _load_like_songs(self) -> bool:
        return self._load_playlist_songs('tracks.json')

    def _load_playlist_songs(self, filename: str) -> bool:
        db_file = utils.get_db_cache_file(filename)
        if os.path.isfile(db_file):
            with open(db_file, 'r') as fp:
                data = fp.read()
            songs = json.loads(data)
            self._track_infos = { x['id']: x for x in songs }
            self._exec_js('cloudUpdateTrackInfos', songs)
            logger.debug(f'load songs from cache: {os.path.basename(db_file)}')
            return True
        return False

    def _save_cache(self, filename: str, data: Any):
        json_data = json.dumps(data)
        with open(utils.get_db_cache_file(filename), 'w') as fp:
            fp.write(json_data)

    def _save_like_songs(self, songs):
        self._save_cache('tracks.json', songs)

    def _save_playlists(self, playlists):
        self._save_cache('playlists.json', playlists)

    def _save_playlist_songs(self, playlist_id, songs):
        self._save_cache(f'tracks_{playlist_id}.json', songs)

    def refresh_playlists(self):
        if not self._logined:
            logger.debug('refresh playlists require login')
            return
        self._js_post(self._api.get_user_playlist, 'cloudUpdatePlaylists', self._handle_playlists)

    def _handle_playlists(self, playlists, _):
        if not playlists:
            logger.debug('refresh playlist failed')
            return

        self._user_playlists = playlists
        logger.debug(f'refresh playlists result, cout: {len(playlists)}')
        self._save_playlists(playlists)
        self._like_playlist_id = playlists[0]['id']
        if not self._current_playlist_id:
            self._current_playlist_id = self._like_playlist_id

        logger.debug(f'refresh current playlist: {self._current_playlist_id} songs')
        self.refresh_playlist_songs(self._current_playlist_id)
        return playlists

    def refresh_playlist_songs(self, playlist_id: int):
        logger.debug(f'start refresh playlist songs, playlist: {playlist_id}')
        self._thread_post(self._api.get_playlist_songs,
                          self._handle_playlist_songs,
                          playlist_id,
                          playlist_id)

    def _handle_playlist_songs(self, songs, playlist_id):
        if not songs:
            logger.error(f'refresh playlist: {playlist_id} failed')
            return

        logger.debug(f'refresh playlist: {playlist_id} success, cache it')
        if playlist_id == self._like_playlist_id:
            self._save_like_songs(songs)
        else:
            self._save_playlist_songs(playlist_id, songs)

        if self._current_playlist_id == playlist_id:
            logger.debug(f'update current playlist track infos, playlist: {playlist_id}')
            self._track_infos = {x['id']: x for x in songs }
            self._exec_js('cloudUpdateTrackInfos', songs)

    def get_track_info(self, song_id):
        song_id = int(song_id)
        return self._track_infos.get(song_id, None)

    def get_playlist_songs(self, playlist_id):
        playlist_id = int(playlist_id)
        self._current_playlist_id = playlist_id
        logger.debug(f'try load playlist: {playlist_id} songs from cache')
        if not self._load_playlist_songs(f'tracks_{playlist_id}.json'):
            logger.debug(f'load playlist: {playlist_id} cache failed, start fetch from net')
            self.refresh_playlist_songs(playlist_id)

    def fetch_track_audio_source(self, song_id, track_unikey):
        logger.debug(f'fetch track audio source, song_id: {song_id}')
        song_id = int(song_id)

        info = self.get_track_info(song_id)
        if not info:
            return

        mp3_name = f"{info['artist']}_{info['name']}.mp3"
        cache_mp3_file = self.get_music_cache_file(mp3_name)
        song_status = info.get('status', True)
        if os.path.exists(cache_mp3_file):
            self._exec_js('cloudUpdateTrackAudioSource', cache_mp3_file)
        else:
            self._cache_quality_mp3(song_id, mp3_name, song_status)
            if song_status:
                self._thread_post(self.get_song_url, self._handle_fetch_audio_source, track_unikey, song_id)
            else:
                self._thread_post(self.get_song_url_by_other_source,
                                  self._handle_fetch_audio_source, track_unikey, song_id)

    def get_song_url(self, song_id: int):
        url = self._api.get_song_url(song_id)
        if url:
            return url
        return self.get_song_url_by_other_source(song_id)

    def get_song_url_by_other_source(self, song_id: int):
        info = self.get_track_info(song_id)
        if not info:
            return None
        name = info['name']
        logger.debug(f'fetch song_id: {song_id}, name: {name} from other source')
        return music_service.fetch_song_url(name, info['artist'], info['album'])

    def _handle_fetch_audio_source(self, url, track_unikey):
        if not url:
            url = ''
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
        self._logined = True
        logger.info('notify user login success')
        self._exec_js('cloudUpdateLoginState', True)

        logger.info('start refresh playlists')
        self.refresh_playlists()

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

    def _cache_quality_mp3(self, song_id: int, mp3_name: str, status: bool):
        if self._current_playlist_id == self._like_playlist_id:
            self._cache_queue.put((song_id, mp3_name, status))

    def _start_cache_mp3_task(self):
        while True:
            task = self._cache_queue.get()
            if task:
                try:
                    song_id, mp3_name, status = task
                    if status:
                        url = self._api.get_exhigh_song_url(song_id)
                    else:
                        url = self.get_song_url_by_other_source(song_id)
                    if url:
                        temp_file = utils.get_temp_cache_file(mp3_name)
                        if utils.download_file(url, temp_file):
                            mp3_file = self.get_music_cache_file(mp3_name)
                            shutil.move(temp_file, mp3_file)
                except Exception as e:
                    logger.exception(f'cache mp3 task, failed: {e}')
            time.sleep(2)
