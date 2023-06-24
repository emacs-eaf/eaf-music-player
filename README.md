### EAF Music Player
<p align="center">
  <img width="800" src="./screenshot.png">
</p>

Music Player application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application

[Install EAF](https://github.com/emacs-eaf/emacs-application-framework#install) first, then add below code in your emacs config:

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/emacs-application-framework/")
(require 'eaf)
(require 'eaf-music-player)
```

### Usage

* `eaf-open-music-player`: Open EAF music player with local directory.
* `eaf-open-cloud-music`: Open EAF music player with Netease favorite list, only for Chinese user.

### Dependency List

| Package                     | Description            |
| :--------                   | :------                |
| python-pytaglib, mutagen    | Parse ID3 tag          |
| certifi, pycryptodome, rsa, | Fetch Lyrics and Cover |
| album-art                   | Fetch Lyrics           |
| Pillow                      | Parse Cover Pixel      |

### The keybinding of EAF Music Player.

| Key   | Event   |
| :---- | :------ |
| `<f12>` | open_devtools |
| `j` | js_play_next |
| `k` | js_play_prev |
| `h` | js_play_random |
| `,` | js_backward |
| `.` | js_forward |
| `SPC` | js_toggle_play_status |
| `C-n` | js_scroll_up |
| `C-p` | js_scroll_down |
| `C-v` | js_scroll_up_page |
| `M-v` | js_scroll_down_page |
| `M-<` | js_scroll_to_begin |
| `M->` | js_scroll_to_bottom |
| `g` | js_jump_to_file |
| `t` | js_toggle_play_order |
| `C-e` | js_sort_by_title |
| `C-t` | js_sort_by_artist |
| `C-m` | js_sort_by_album |
| `C-l` | js_change_panel |
| `C-u` | js_toggle_play_source |
| `C-s` | search_text_forward |
| `C-r` | search_text_backward |
| `F` | open_link |
| `e` | edit_tag_info |
| `s` | show_tag_info |
| `T` | convert_tag_coding |
| `r` | refresh_cloud_tracks |
| `p` | playlist_prev |
| `n` | playlist_next |


