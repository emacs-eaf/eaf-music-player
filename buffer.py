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

import colorsys
import hashlib
import mimetypes
import os
import random
import sys
from functools import cmp_to_key

import taglib
from core.utils import *
from core.webengine import BrowserBuffer  # type: ignore
from PIL import Image
from PyQt6 import QtCore
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QColor

try:
    from mutagen.easyid3 import EasyID3
except ImportError:
    EasyID3 = None

sys.path.append(os.path.dirname(__file__))
from music_service import music_service
from music_service.utils import get_logger

log = get_logger('AppBuffer')

class PlaySourceType:
    Local = 'local'
    Cloud = 'cloud'


class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.play_source = PlaySourceType.Local
        self.play_track_key = ''

        self.local_tracks = {}
        self.thread_queue = []

        self.first_file = os.path.expanduser(url)
        self.panel_background_color = QColor(self.theme_background_color).darker(110).name()
        self.icon_dir = os.path.join(os.path.dirname(__file__), "src", "svg")
        self.icon_cache_dir = os.path.join(os.path.dirname(__file__), "src", "svg_cache")
        self.cover_cache_dir = os.path.join(os.path.dirname(__file__), "src", "cover_cache")
        self.lyrics_cache_dir = os.path.join(os.path.dirname(__file__), "src", "lyrics_cache")
        self.light_cover_path = os.path.join(os.path.dirname(__file__), "src", "cover", "light_cover.svg")
        self.dark_cover_path = os.path.join(os.path.dirname(__file__), "src", "cover", "dark_cover.svg")

        self.theme_background_rgb_color = hex_to_rgb(self.theme_background_color)

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

        track_list = self.pick_music_info(files)
        self.local_tracks = {x['path']:x for x in track_list}
        self.buffer_widget.eval_js_function('addLocalTrackInfos', track_list)

    def get_default_cover_path(self):
        return self.light_cover_path if self.theme_mode == "light" else self.dark_cover_path

    @QtCore.pyqtSlot(str, str)
    def vue_update_current_track(self, play_source, play_track_key):
        log.debug(f'start play source: {play_source}, key: {play_track_key}')
        self.play_source = play_source
        self.play_track_key = play_track_key

        track_infos = self.get_current_play_track_info()
        self.fetch_cover(track_infos)
        self.fetch_lyric(track_infos)

    def get_current_track_unikey(self):
        return f'{self.play_source}_{self.play_track_key}'

    def is_current_play_track(self, track_unikey: str) -> bool:
        current_track_unikey = self.get_current_track_unikey()
        return current_track_unikey == track_unikey

    def is_local_source(self):
        return self.play_source == PlaySourceType.Local

    def get_current_play_track_info(self):
        track_unikey = self.get_current_track_unikey()
        infos = self.local_tracks[self.play_track_key]
        infos['unikey'] = track_unikey
        return infos

    def _get_tag_value(self, tags, key: str) -> str:
        values = tags.get(key, None)
        if not values:
            return ''
        return values[0]

    def get_audio_taginfos(self, file_path: str) -> dict:
        tags = taglib.File(file_path).tags
        title_key = 'TITLE'
        artist_key = 'ARTIST'
        album_key = 'ALBUM'
        if not self._get_tag_value(tags, title_key):
            if EasyID3 is not None:
                try:
                    tags = EasyID3(file_path)
                    title_key = title_key.lower()
                    artist_key = artist_key.lower()
                    album_key = album_key.lower()
                except Exception:
                    pass
        title = self._get_tag_value(tags, title_key)
        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0]
        return {
            'path': file_path,
            'title': title,
            'artist': self._get_tag_value(tags, artist_key),
            'album': self._get_tag_value(tags, album_key)
        }

    def fetch_cover(self, infos):
        artist = infos['artist']
        title = infos['name']
        album = infos['album']
        unikey = infos['unikey']
        cover_path = get_cover_path(self.cover_cache_dir, artist, title)

        # Fill default cover if no match cover found.
        if not os.path.exists(cover_path):
            self.buffer_widget.eval_js_function("updateCover", self.get_default_cover_path())
            self.buffer_widget.eval_js_function("updateLyricColor", "#CCCCCC")
            fetch_cover_thread = FetchCover(unikey, self.cover_cache_dir, artist, title, album)
            fetch_cover_thread.fetch_result.connect(self.update_cover)
            fetch_cover_thread.fetch_failed.connect(self.update_audio_motion_gradient)
            self.thread_queue.append(fetch_cover_thread)
            fetch_cover_thread.start()
        else:
            self.update_cover(unikey, cover_path)

    def fetch_lyric(self, infos):
        self.buffer_widget.eval_js_function("updateLyric", "")

        title = infos['name']
        artist = infos['artist']
        album = infos['album']
        unikey = infos['unikey']
        lyric_path = get_lyric_path(self.lyrics_cache_dir, artist, title)

        if os.path.exists(lyric_path):
            with open(lyric_path, "r") as f:
                self.update_lyric(unikey, f.read())
        else:
            self.update_lyric(unikey, '[99:00.000]正在搜索歌词，请稍等')
            fetch_lyric_thread = FetchLyric(unikey, self.lyrics_cache_dir, title, artist, album)
            fetch_lyric_thread.fetch_result.connect(self.update_lyric)
            self.thread_queue.append(fetch_lyric_thread)
            fetch_lyric_thread.start()

    def update_lyric(self, track_unikey, lyric):
        # Only update lyric when
        if self.is_current_play_track(track_unikey):
            self.buffer_widget.eval_js_function("updateLyric", string_to_base64(lyric))

    def update_cover(self, track_unikey, url):
        # Only update cover when
        if self.is_current_play_track(track_unikey):
            self.buffer_widget.eval_js_function("updateCover", url)
            self.buffer_widget.eval_js_function("updateLyricColor",
                                                "#3F3F3F" if is_light_image(url) else "#CCCCCC")
            self.update_audio_motion_gradient(url)

    def update_audio_motion_gradient(self, url=None):
        try:
            tags = self.get_current_play_track_info()
            title = tags['name']
            color_list = get_color(url, title, self.theme_background_rgb_color)
            self.buffer_widget.eval_js_function("setAudioMotion", color_list)
        except Exception as e:
            log.exception(f'auido motion get color failed: {e}')

    def pick_music_info(self, files):
        infos = []

        for file in files:
            file_type = mimetypes.guess_type(file)[0]
            if file_type and file_type.startswith("audio/"):
                tags = self.get_audio_taginfos(file)
                tags['name'] = tags['title']
                del tags['title']
                infos.append(tags)

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
        info = self.get_current_play_track_info()
        log.debug(f"Tag info: {info['name']} / {info['artist']} / {info['album']} ")

    def convert_tag_coding(self):
        if not self.is_local_source():
            message_to_emacs('only support local play source')
            return
        info = self.get_current_play_track_info()
        name = self.convert_to_utf8(info["name"])
        artist = self.convert_to_utf8(info["artist"])
        album = self.convert_to_utf8(info["album"])
        track_path = info["path"]
        self.write_tag_info(track_path, name, artist, album)
        self.buffer_widget.eval_js_function("updateTagInfo", track_path, name, artist, album)
        message_to_emacs(f"Convert tag info to: {name} / {artist} / {album}")

    def edit_tag_info(self):
        if not self.is_local_source():
            message_to_emacs('only support local play source')
            return
        info = self.get_current_play_track_info()
        eval_in_emacs('eaf-music-player-edit-tag-info',
                      [self.buffer_id, info["name"], info["artist"], info["album"]])

    @PostGui()
    def update_tag_info(self, tag_str):
        if not self.is_local_source():
            message_to_emacs('only support local play source')
            return

        info = self.get_current_play_track_info()
        track_path = info['path']
        tag_info = tag_str.split("\n")
        name = tag_info[0] if len(tag_info) > 0 else ""
        artist = tag_info[1] if len(tag_info) > 1 else ""
        album = tag_info[2] if len(tag_info) > 2 else ""

        self.write_tag_info(track_path, name, artist, album)
        self.buffer_widget.eval_js_function("updateTagInfo", track_path, name, artist, album)
        message_to_emacs(f"Update tag info: {name} / {artist} / {album}")

    def convert_to_utf8(self, gbk_str):
        try:
            return gbk_str.encode('latin1').decode('gbk')
        except UnicodeEncodeError:
            return gbk_str
        except UnicodeDecodeError:
            return gbk_str

class FetchCover(QThread):
    fetch_result = QtCore.pyqtSignal(str, str)
    fetch_failed = QtCore.pyqtSignal()

    def __init__(self, track_unikey, cover_cache_dir, artist, title, album):
        QThread.__init__(self)

        self.track_unikey = track_unikey
        self.cover_cache_dir = cover_cache_dir
        self.artist = artist
        self.title = title
        self.album = album

    def run(self):
        if not os.path.exists(self.cover_cache_dir):
            os.makedirs(self.cover_cache_dir)

        cover_path = get_cover_path(self.cover_cache_dir, self.artist, self.title)

        if os.path.exists(cover_path):
            self.fetch_result.emit(self.track_unikey, cover_path)
        else:
            result = music_service.fetch_cover(cover_path, self.title, self.artist, self.album)
            if result:
                self.fetch_result.emit(self.track_unikey, cover_path)
            else:
                log.error(f"Fetch cover name for {self.title} failed.")
                self.fetch_failed.emit()

class FetchLyric(QThread):
    fetch_result = QtCore.pyqtSignal(str, str)

    def __init__(self, track_unikey, cache_dir, title, artist, album):
        QThread.__init__(self)

        self.track_unikey = track_unikey
        self.lyrics_cache_dir = cache_dir
        self.title = title
        self.artist = artist
        self.album = album

    def run(self):
        result = music_service.fetch_lyric(self.title, self.artist, self.album)
        if result:
            lyric_path = get_lyric_path(self.lyrics_cache_dir, self.artist, self.title)
            with open(lyric_path, "w") as f:
                f.write(result)
        else:
            result = '[99:00.000]暂无歌词，请欣赏'
        self.fetch_result.emit(self.track_unikey, result)


def get_lyric_path(lyrics_cache_dir, artist, title):
    return os.path.join(lyrics_cache_dir, "{}_{}.lyc".format(artist.replace("/", "_"), title.replace("/", "_")))

def get_cover_path(cover_cache_dir, artist, title):
    return os.path.join(cover_cache_dir, "{}_{}.png".format(artist.replace("/", "_"), title.replace("/", "_")))

def is_light_image(img_path):
    try:
        img = Image.open(img_path)
        width, height = img.size

        left = int(width * 0.25)
        right = int(width * 0.75)
        top = int(height * 0.25)
        bottom = int(height * 0.75)

        pixels = []
        for i in range(top, bottom):
            for j in range(left, right):
                pixel = img.getpixel((j, i))
                pixels.append(pixel)

        light_pixels = 0
        for pixel in pixels:
            r, g, b = pixel[:3]
            if r > 220 or g > 220 or b > 220:
                light_pixels += 1

        light_pixel_ratio = light_pixels / len(pixels)
        return light_pixel_ratio > 0.45
    except Exception as e:
        log.exception(f'check is light image error: {e}')
        return False

def color_is_similar(color, new_color, similarity_threshold):
    distance = ((new_color[0] - color[0]) ** 2 + (new_color[1] - color[1]) ** 2 + (new_color[2] - color[2]) ** 2) ** 0.5
    return distance < similarity_threshold

def relative_luminance(color):
    color = color[:3]  # fix rgba error
    r, g, b = (c / 255 for c in color)
    gamma_corrected = tuple(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055)**2.4 for c in (r, g, b))
    return 0.2126 * gamma_corrected[0] + 0.7152 * gamma_corrected[1] + 0.0722 * gamma_corrected[2]

def contrast_ratio(color1, color2):
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    return (l1 + 0.05) / (l2 + 0.05) if l1 > l2 else (l2 + 0.05) / (l1 + 0.05)

def get_color(img_path, title, background_color):
    results = []

    if img_path:
        if not os.path.exists(img_path):
            return []
        img = Image.open(img_path)

        width, height = img.size
        colors = img.getcolors(width * height)
        colors = sorted(colors, key=lambda x: -x[0])

        new_colors = [colors[0]]
        for color in colors[1:]:
            is_similar = False
            for new_color in new_colors:
                if color_is_similar(color[1], new_color[1], 100):
                    is_similar = True
                    break

            if not is_similar:
                new_colors.append(color)

            if len(new_colors) == 10:
                break

        sorted_colors = []
        for count, rgb_color in new_colors:
            hsl_color = colorsys.rgb_to_hls(rgb_color[0] / 255, rgb_color[1] / 255, rgb_color[2] / 255)

            # Color won't add to audio gradient if color match below rules:
            # 1. The color is too bright
            # 2. The color is too dark
            # 3. The contrast between the color and the emacs background color is too low
            if hsl_color[1] > 0.1 and hsl_color[2] > 0.1 and hsl_color[2] < 0.8 and contrast_ratio(rgb_color, background_color) > 2:
                sorted_colors.append((count, rgb_color, hsl_color))
        sorted_colors = sorted(sorted_colors, key=lambda x: (x[2][0], -x[2][1], -x[2][2]))

        for count, rgb_color, _ in sorted_colors:
            hex_color = "#{:02x}{:02x}{:02x}".format(rgb_color[0], rgb_color[1], rgb_color[2])
            results.append(hex_color)

    if len(results) < 2:
        results = generate_colors(title, background_color)

    return results

def hex_to_rgb(hex_color):
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    if len(hex_color) != 6:
        return None

    return tuple(int(hex_color[i:i+2], 16) for i in range(0, 6, 2))

def rgb_to_hex(rgb_color):
    return '#' + ''.join([format(c, '02x') for c in rgb_color])

def generate_colors(song_name, bg_color):
    random.seed(hashlib.md5(song_name.encode('utf-8')).hexdigest())
    colors = []

    def random_color():
        h = random.uniform(0, 1)
        s = random.uniform(0.5, 1)
        v = random.uniform(0.1, 0.8)
        return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

    while True:
        candidates = [random_color() for _ in range(100)]

        for new_color in candidates:
            if contrast_ratio(new_color, bg_color) > 2:
                colors.append(rgb_to_hex(new_color))

            if len(colors) > 4:
                return colors

    return colors
