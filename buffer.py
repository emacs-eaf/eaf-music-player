#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt6 import QtCore
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QColor
from core.webengine import BrowserBuffer    # type: ignore
from functools import cmp_to_key
from core.utils import *
from PIL import Image
import shutil
import os
import mimetypes
import taglib
import subprocess
import time
import base64
import requests
from urllib.parse import quote_plus
from typing import Optional

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.vue_current_track = ""

        self.music_infos = []
        self.thread_queue = []

        self.first_file = os.path.expanduser(url)
        self.panel_background_color = QColor(self.theme_background_color).darker(110).name()
        self.icon_dir = os.path.join(os.path.dirname(__file__), "src", "svg")
        self.icon_cache_dir = os.path.join(os.path.dirname(__file__), "src", "svg_cache")
        self.cover_cache_dir = os.path.join(os.path.dirname(__file__), "src", "cover_cache")
        self.lyrics_cache_dir = os.path.join(os.path.dirname(__file__), "src", "lyrics_cache")
        self.light_cover_path = os.path.join(os.path.dirname(__file__), "src", "cover", "light_cover.svg")
        self.dark_cover_path = os.path.join(os.path.dirname(__file__), "src", "cover", "dark_cover.svg")
        self.lyric_js = os.path.join(os.path.dirname(__file__), "lyric.js")

        if not os.path.exists(self.lyrics_cache_dir):
            os.makedirs(self.lyrics_cache_dir)
        if not os.path.exists(self.icon_cache_dir):
            os.makedirs(self.icon_cache_dir)

        self.init_icons()

        self.change_title(get_emacs_var("eaf-music-player-buffer"))

        self.load_index_html(__file__)

    def init_icons(self):
        # Change svg file color on Python side, it's hard to change svg color on JavaScript.
        for svg in os.listdir(self.icon_dir):
            with open(os.path.join(self.icon_dir, svg), encoding="utf-8", errors="ignore") as f:
                svg_content = f.read().replace("<path", '''<path fill="{}"'''.format(self.theme_foreground_color))
                with open(os.path.join(self.icon_cache_dir, svg), "w") as svg_file:
                    svg_file.write(svg_content)

    @interactive
    def update_theme(self):
        super().update_theme()
        self.panel_background_color = QColor(self.theme_background_color).darker(110).name()

        self.init_icons()
        self.init_vars()

    def init_vars(self):
        self.buffer_widget.eval_js_function(
            '''initPlaylist''',
            self.theme_background_color,
            self.theme_foreground_color)

        self.buffer_widget.eval_js_function(
            '''initPanel''',
            get_emacs_var("eaf-music-play-order"),
            self.panel_background_color,
            self.theme_foreground_color,
            self.icon_cache_dir,
            self.cover_cache_dir,
            os.path.sep,
            self.get_default_cover_path()
        )

    def init_app(self):
        self.init_vars()

        files = []

        if os.path.isdir(self.first_file):
            files = list(filter(lambda f : os.path.isfile(f),
                                [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.first_file) for f in filenames]))
        elif os.path.isfile(self.first_file):
            files.append(self.first_file)

        self.music_infos = self.pick_music_info(files)

        self.buffer_widget.eval_js_function('''addFiles''', self.music_infos)

    def get_default_cover_path(self):
        return self.light_cover_path if self.theme_mode == "light" else self.dark_cover_path

    @QtCore.pyqtSlot(str)
    def vue_update_current_track(self, current_track):
        self.vue_current_track = current_track

        self.fetch_cover(current_track)
        self.fetch_lyric(current_track)

    def fetch_cover(self, current_track):
        tags = taglib.File(current_track).tags
        artist = self.pick_tag_artist(tags)
        title = self.pick_tag_title(current_track, tags)
        cover_path = get_cover_path(self.cover_cache_dir, artist, title)

        # Fill default cover if no match cover found.
        if not os.path.exists(cover_path):
            self.buffer_widget.eval_js_function("updateCover", self.get_default_cover_path())

        if shutil.which("album-art"):
            fetch_cover_thread = FetchCover(current_track, self.cover_cache_dir, artist, title)
            fetch_cover_thread.fetch_result.connect(self.update_cover)
            self.thread_queue.append(fetch_cover_thread)
            fetch_cover_thread.start()
        else:
            print("Please run `sudo npm i -g album-art' package to fetch cover.")

    def fetch_lyric(self, current_track):
        self.buffer_widget.eval_js_function("updateLyric", "")

        tags = taglib.File(current_track).tags
        title = self.pick_tag_title(current_track, tags)
        artist = self.pick_tag_artist(tags)
        album = self.pick_tag_album(tags)
        lyric_path = get_lyric_path(self.lyrics_cache_dir, artist, title)

        if os.path.exists(lyric_path):
            with open(lyric_path, "r") as f:
                self.update_lyric(current_track, f.read())
        else:
            fetch_lyric_thread = FetchLyric(current_track, self.lyric_js, self.lyrics_cache_dir, title, artist, album)
            fetch_lyric_thread.fetch_result.connect(self.update_lyric)
            self.thread_queue.append(fetch_lyric_thread)
            fetch_lyric_thread.start()

    def update_lyric(self, track, lyric):
        # Only update cover when
        if track == self.vue_current_track:
            self.buffer_widget.eval_js_function("updateLyric", string_to_base64(lyric))

    def update_cover(self, track, url):
        # Only update cover when
        if track == self.vue_current_track:
            self.buffer_widget.eval_js_function("updateCover", url)

            self.buffer_widget.eval_js_function("updateLyricColor", "#3F3F3F" if is_light_image(url) else "#CCCCCC")


    def pick_tag_title(self, file, tags):
        return tags["TITLE"][0].strip() if "TITLE" in tags and len(tags["TITLE"]) > 0 else os.path.splitext(os.path.basename(file))[0]

    def pick_tag_artist(self, tags):
        return tags["ARTIST"][0].strip() if "ARTIST" in tags and len(tags["ARTIST"]) > 0 else ""

    def pick_tag_album(self, tags):
        return tags["ALBUM"][0].strip() if "ALBUM" in tags and len(tags["ALBUM"]) > 0 else ""

    def pick_music_info(self, files):
        infos = []

        for file in files:
            file_type = mimetypes.guess_type(file)[0]
            if file_type and file_type.startswith("audio/"):
                tags = taglib.File(file).tags

                info = {
                    "name": self.pick_tag_title(file, tags),
                    "path": file,
                    "artist": self.pick_tag_artist(tags),
                    "album": self.pick_tag_album(tags)
                }
                infos.append(info)

        infos.sort(key=cmp_to_key(self.music_compare))

        return infos

    def music_compare(self, a, b):
        if a["artist"] < b["artist"]:
            return -1
        elif a["artist"] > b["artist"]:
            return 1
        else:
            if a["album"] < b["album"]:
                return -1
            elif a["album"] > b["album"]:
                return 1
            else:
                return 0

    def write_tag_info(self, path, name, artist, album):
        audio = taglib.File(path)
        audio.tags['TITLE'] = name
        audio.tags['ARTIST'] = artist
        audio.tags['ALBUM'] = album
        audio.save()

    def show_tag_info(self):
        for info in self.music_infos:
            if info["path"] == self.vue_current_track:
                message_to_emacs(f"Tag info: {info['name']} / {info['artist']} / {info['album']} ")
                break

    def convert_tag_coding(self):
        for info in self.music_infos:
            if info["path"] == self.vue_current_track:
                name = self.convert_to_utf8(info["name"])
                artist = self.convert_to_utf8(info["artist"])
                album = self.convert_to_utf8(info["album"])

                self.write_tag_info(self.vue_current_track, name, artist, album)

                self.buffer_widget.eval_js_function("updateTagInfo", self.vue_current_track, name, artist, album)

                message_to_emacs(f"Convert tag info to: {name} / {artist} / {album}")
                break

    def edit_tag_info(self):
        for info in self.music_infos:
            if info["path"] == self.vue_current_track:
                eval_in_emacs('eaf-music-player-edit-tag-info', [self.buffer_id, info["name"], info["artist"], info["album"]])
                break

    @PostGui()
    def update_tag_info(self, tag_str):
        tag_info = tag_str.split("\n")

        name = tag_info[0] if len(tag_info) > 0 else ""
        artist = tag_info[1] if len(tag_info) > 1 else ""
        album = tag_info[2] if len(tag_info) > 2 else ""

        self.write_tag_info(self.vue_current_track, name, artist, album)

        self.buffer_widget.eval_js_function("updateTagInfo", self.vue_current_track, name, artist, album)

        message_to_emacs(f"Update tag info: {name} / {artist} / {album}")

    def convert_to_utf8(self, gbk_str):
        try:
            return gbk_str.encode('latin1').decode('gbk')
        except UnicodeDecodeError:
            return gbk_str

class FetchCover(QThread):

    fetch_result = QtCore.pyqtSignal(str, str)

    def __init__(self, track, cover_cache_dir, artist, title):
        QThread.__init__(self)

        self.track = track
        self.cover_cache_dir = cover_cache_dir
        self.artist = artist
        self.title = title

    def run(self):
        if not os.path.exists(self.cover_cache_dir):
            os.makedirs(self.cover_cache_dir)

        cover_path = get_cover_path(self.cover_cache_dir, self.artist, self.title)

        if os.path.exists(cover_path):
            self.fetch_result.emit(self.track, cover_path)
        else:
            import subprocess
            result = subprocess.run(
                "album-art '{}' '{}'".format(self.artist, self.title),
                shell=True, capture_output=True, text=True).stdout

            import urllib.request
            try:
                urllib.request.urlretrieve(result, cover_path)
                self.fetch_result.emit(self.track, cover_path)
            except:
                print("Fetch cover for {} failed.".format(self.track))

class FetchLyric(QThread):
    fetch_result = QtCore.pyqtSignal(str, str)

    def __init__(self, track, lyric_js, cache_dir, title, artist, album):
        QThread.__init__(self)

        self.track = track
        self.lyric_js = lyric_js
        self.lyrics_cache_dir = cache_dir
        self.title = title
        self.artist = artist
        self.album = album

    def get_lyric_from_netease(self):
        node_process = subprocess.Popen(['node', self.lyric_js, self.title, self.artist, self.album],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        output, _ = node_process.communicate()

        return output.decode('utf-8')

    def get_lyric_from_qq_music(self):
        try:
            api = QQMusicLyric()
            return api.query_lyric(self.title, self.artist).decode("utf-8")
        except:
            return None

    def run(self):
        result = self.get_lyric_from_qq_music()
        if result is None:
            result = self.get_lyric_from_netease()

        lyric_path = get_lyric_path(self.lyrics_cache_dir, self.artist, self.title)
        with open(lyric_path, "w") as f:
            f.write(result)

        self.fetch_result.emit(self.track, result)

class QQMusicLyric:

    def query_lyric(self, name: str, artist: Optional[str] = "") -> Optional[str]:
        mid = self._search_song(name, artist)
        if not mid:
            return None
        return self._download_lyric(mid)

    def _search_song(self, name: str, artist: Optional[str] = "") -> Optional[str]:
        key = quote_plus(f"{name} {artist}".strip())
        url = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?format=json" \
              "&inCharset=utf-8&outCharset=utf-8&key=" + key
        try:
            result = requests.get(url, headers={"Referer": "https://c.y.qq.com/"}).json()
        except Exception as e:
            print(f"query name: {name}, artist: {artist} lyric fail: {e}")
            result = {}
        item_list = result.get("data", {}).get("song", {}).get("itemlist", None)
        if not item_list:
            return None
        return item_list[0].get("mid", None)

    def _download_lyric(self, mid: str) -> Optional[str]:
        if not mid:
            return None
        current_millis = int((time.time()) * 1000)
        data = {
            'pcachetime': str(current_millis),
            'songmid': mid,
            'g_tk': '5381',
            'loginUin': '0',
            'hostUin': '0',
            'format': 'json',
            'inCharset': 'utf8',
            'outCharset': 'utf8',
            'notice': '0',
            'platform': 'yqq',
            'needNewCode': '0',
        }

        url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        headers = {
                'Referer': 'https://c.y.qq.com/'
        }
        try:
            result = requests.post(url, data=data, headers=headers).json()
        except Exception as e:
            print(f"[qqmusic lyric] download mid: {mid} fail: {e}")
            result = {}

        lyric = result.get("lyric", None)
        if not lyric:
            return None
        return base64.b64decode(lyric).decode("utf-8")

def get_lyric_path(lyrics_cache_dir, artist, title):
    return os.path.join(lyrics_cache_dir, "{}_{}.lyc".format(artist.replace("/", "_"), title.replace("/", "_")))

def get_cover_path(cover_cache_dir, artist, title):
    return os.path.join(cover_cache_dir, "{}_{}.png".format(artist.replace("/", "_"), title.replace("/", "_")))

def is_light_image(img_path):
    try:
        img = Image.open(img_path)
        pixels = list(img.getdata())

        total_pixels = len(pixels)
        light_pixels = 0

        for pixel in pixels:
            r, g, b = pixel  # Extract R, G, B values
            if r > 220 or g > 220 or b > 220:
                light_pixels += 1

        light_pixel_ratio = light_pixels / total_pixels
        return light_pixel_ratio > 0.6
    except:
        return False
