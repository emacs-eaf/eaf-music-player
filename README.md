### EAF Music Player
<p align="center">
  <img width="800" src="./screenshot.png">
</p>

Music Player application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/eaf-music-player/")
(require 'eaf-music-player)
```

### Dependency List

| Package         | Description   |
| :--------       | :------       |
| python-pytaglib | Parse ID3 tag |
