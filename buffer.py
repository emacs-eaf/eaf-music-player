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
from PyQt6.QtGui import QColor
from core.webengine import BrowserBuffer    # type: ignore
from functools import cmp_to_key
from core.utils import get_emacs_var, interactive, get_emacs_theme_foreground, get_emacs_theme_background, message_to_emacs
import os
import mimetypes
import taglib

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.music_infos = []

        self.first_file = os.path.expanduser(url)
        self.panel_background_color = QColor(self.theme_background_color).darker(110).name()
        self.icon_dir = os.path.join(os.path.dirname(__file__), "src", "svg")
        self.icon_cache_dir = os.path.join(os.path.dirname(__file__), "src", "svg_cache")
        if not os.path.exists(self.icon_cache_dir):
            os.makedirs(self.icon_cache_dir)

        self.init_icons()
        
        self.change_title("EAF Music Player")

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
            os.path.sep
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

    def pick_music_info(self, files):
        infos = []

        for file in files:
            file_type = mimetypes.guess_type(file)[0]
            if file_type and file_type.startswith("audio/"):
                tags = taglib.File(file).tags

                info = {
                    "name": tags["TITLE"][0].strip() if "TITLE" in tags and len(tags["TITLE"]) > 0 else os.path.splitext(os.path.basename(file))[0],
                    "path": file,
                    "artist": tags["ARTIST"][0].strip() if "ARTIST" in tags and len(tags["ARTIST"]) > 0 else "",
                    "album": tags["ALBUM"][0].strip() if "ALBUM" in tags and len(tags["ALBUM"]) > 0 else ""
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

    @QtCore.pyqtSlot(str)
    def show_tag_info(self, track):
        for info in self.music_infos:
            if info["path"] == track:
                message_to_emacs(f"Tag info: {info['name']} / {info['artist']} / {info['album']} ")
                break

    @QtCore.pyqtSlot(str)
    def convert_tag_coding(self, track):
        for info in self.music_infos:
            if info["path"] == track:
                name = self.convert_to_utf8(info["name"])
                artist = self.convert_to_utf8(info["artist"])
                album = self.convert_to_utf8(info["album"])

                audio = taglib.File(track)
                audio.tags['TITLE'] = name
                audio.tags['ARTIST'] = artist
                audio.tags['ALBUM'] = album
                audio.save()

                self.buffer_widget.eval_js_function("updateTagInfo", track, name, artist, album)

                message_to_emacs(f"Convert tag info to: {name} / {artist} / {album}")
                break

    def convert_to_utf8(self, gbk_str):
        try:
            return gbk_str.encode('latin1').decode('gbk')
        except UnicodeDecodeError:
            return gbk_str
