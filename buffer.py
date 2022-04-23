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
from PyQt6.QtCore import QUrl
from core.webengine import BrowserBuffer
from core.utils import interactive
from functools import cmp_to_key
from core.utils import eval_in_emacs, get_emacs_var, message_to_emacs
import os
import json
import mimetypes
import taglib

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.first_file = os.path.expanduser(url)
        self.panel_background_color = QColor(self.theme_background_color).darker(110).name()
        
        self.change_title("EAF Music Player")

        self.load_index_html(__file__)

    def init_app(self):
        self.buffer_widget.eval_js_function('''initPlaylistColor''', self.theme_background_color, self.theme_foreground_color)

        self.buffer_widget.eval_js_function('''initPanelColor''', self.panel_background_color, self.theme_foreground_color)

        self.buffer_widget.eval_js_function('''initPlayOrder''', get_emacs_var("eaf-music-play-order"))

        files = []

        if os.path.isdir(self.first_file):
            files = list(filter(lambda f : os.path.isfile(f), [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.first_file) for f in filenames]))
        elif os.path.isfile(self.first_file):
            files.append(self.first_file)

        self.buffer_widget.eval_js_function('''addFiles''', self.pick_music_info(files))

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

    def marker_offset_x(self):
        return 0

    def marker_offset_y(self):
        return 8
