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
import shutil
import os
import mimetypes
import taglib
import subprocess
import threading

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
        self.light_cover_path = os.path.join(os.path.dirname(__file__), "src", "cover", "light_cover.svg")
        self.dark_cover_path = os.path.join(os.path.dirname(__file__), "src", "cover", "dark_cover.svg")

        self.port = get_free_port()
        self.server_js = os.path.join(os.path.dirname(__file__), "server.js")
        server_thread = threading.Thread(target=self.init_server)
        self.thread_queue.append(server_thread)
        server_thread.start()

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

        self.buffer_widget.eval_js_function(
            '''connectServer''',
            self.port)

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

    def init_server(self):
        self.node_process = subprocess.Popen(['node', self.server_js, str(self.port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        try:
            stdout, stderr = self.node_process.communicate(timeout=2)
        except Exception:
            print("The connection to server.js timed out. port:", self.port)

    def get_default_cover_path(self):
        return self.light_cover_path if self.theme_mode == "light" else self.dark_cover_path

    @QtCore.pyqtSlot(str)
    def vue_update_current_track(self, current_track):
        self.vue_current_track = current_track

        tags = taglib.File(current_track).tags

        artist = self.pick_tag_artist(tags)
        title = self.pick_tag_title(current_track, tags)
        cover_path = os.path.join(self.cover_cache_dir, "{}_{}.png".format(artist, title))

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

    def update_cover(self, track, url):
        # Only update cover when
        if track == self.vue_current_track:
            self.buffer_widget.eval_js_function("updateCover", url)

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
        self.artist = artist.replace('/', '_')
        self.title = title.replace('/', '_')

    def run(self):
        if not os.path.exists(self.cover_cache_dir):
            os.makedirs(self.cover_cache_dir)

        cover_path = os.path.join(self.cover_cache_dir, "{}_{}.png".format(self.artist, self.title))

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
                import traceback
                print(traceback.print_exc())
                print("Fetch {} failed.".format(result))
