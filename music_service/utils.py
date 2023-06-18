import logging
import os.path

import requests

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/86.0.4240.30 Safari/537.36'


def download_file(url, filename) -> bool:
    url = url.strip()
    try:
        response = requests.get(url, stream=True)
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    file.write(chunk)
    except Exception as e:
        print(f'download url: {url}, error: {e}')
    return os.path.exists(filename)


def get_logger(name: str) -> logging.Logger:
    log_formatter = logging.Formatter(
        fmt='[eaf-music-player] %(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log_level = 'DEBUG'
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(log_level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    return logger


def get_cookie_cache_file(name: str) -> str:
    cookie_cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'cookie_cache')
    if not os.path.isdir(cookie_cache_dir):
        os.makedirs(cookie_cache_dir)
    return os.path.join(cookie_cache_dir, name)
