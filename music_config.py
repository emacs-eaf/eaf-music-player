import json
import os.path
from typing import Dict, Union


class MusicConfig:
    _config: Dict[str, Union[str, int]]

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._config = {}

        # load config
        self._load()

    def _load(self):
        if os.path.isfile(self._file_path):
            try:
                with open(self._file_path, 'r') as fp:
                    data = fp.read()
                self._config = json.loads(data)
            except:
                pass
        self._load_default()

    def _load_default(self):
        self._config.setdefault('music_source', 'local')
        self._config.setdefault('play_mode', 'random')
        self._config.setdefault('local_track_path', '')
        self._config.setdefault('cloud_playlist_id', 0)
        self._config.setdefault('cloud_track_id', 0)

    def set_config(self, key: str, value: Union[str, int]):
        self._config[key] = value

        # real save
        self._save()

    def _save(self):
        with open(self._file_path, 'w') as fp:
            fp.write(json.dumps(self._config))

    def get_config(self, key: str, default=None) -> Union[str, int]:
        return self._config.get(key, default)

    def is_local_source(self) -> bool:
        return self.music_source == 'local'

    def to_dict(self):
        return self._config

    @property
    def music_source(self):
        return self.get_config('music_source', 'local')

    @music_source.setter
    def music_source(self, val: str):
        if self.music_source != val:
            self.set_config('music_source', val)

    @property
    def play_mode(self):
        return self.get_config('play_mode', '')

    @play_mode.setter
    def play_mode(self, val: str):
        if self.play_mode != val:
            self.set_config('play_mode', val)

    @property
    def local_track_path(self):
        return self.get_config('local_track_path', '')

    @local_track_path.setter
    def local_track_path(self, val: str):
        if self.local_track_path != val:
            self.set_config('local_track_path', val)

    @property
    def cloud_playlist_id(self):
        return self.get_config('cloud_playlist_id', 0)

    @cloud_playlist_id.setter
    def cloud_playlist_id(self, val: str):
        if self.cloud_playlist_id != val:
            self.set_config('cloud_playlist_id', val)

    @property
    def cloud_track_id(self):
        return self.get_config('cloud_track_id', 0)

    @cloud_track_id.setter
    def cloud_track_id(self, val: int):
        if self.cloud_track_id != val:
            self.set_config('cloud_track_id', val)
