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
