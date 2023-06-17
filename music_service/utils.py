import os.path
import requests
import logging

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
