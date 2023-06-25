import logging
import os.path

import requests

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/86.0.4240.30 Safari/537.36'

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


logger = get_logger('Utils')


def _download_file(url, filename) -> bool:
    if not url:
        return False
    url = url.strip()
    response = requests.get(url, stream=True, timeout=5)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                file.write(chunk)
    return os.path.exists(filename)

def download_file(url, filename) -> bool:
    for i in range(3):
        try:
            return _download_file(url, filename)
        except Exception as e:
            logger.exception(f'[eaf-music-player] download file error: {e}')
    return False

def get_cloud_cache_dir():
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'cloud_cache')
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def get_cloud_cache_file(dirname: str, filename: str):
    sub_cache_dir = os.path.join(get_cloud_cache_dir(), dirname)
    if not os.path.isdir(sub_cache_dir):
        os.makedirs(sub_cache_dir)
    return os.path.join(sub_cache_dir, filename)


def get_cookie_cache_file(name: str) -> str:
    return get_cloud_cache_file('cookie', name)

def get_temp_cache_file(name: str) -> str:
    return get_cloud_cache_file('temp', name)

def get_db_cache_file(name: str) -> str:
    return get_cloud_cache_file('db', name)

def get_config_cache_file(name: str) -> str:
    return get_cloud_cache_file('conf', name)
