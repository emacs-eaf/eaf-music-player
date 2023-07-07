import base64
import multiprocessing

import requests
from flask import Flask, Response, request, stream_with_context
from music_service.utils import get_logger

logger = get_logger('BridgeServer')
app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
    'Referer': 'https://www.bilibili.com/'
}

@app.route('/forward', methods=['GET'])
def forward():
    url = request.args.get('url')
    if not url:
        return 'Invalid arguments', 400

    try:
        url = base64.b64decode(url).decode('utf-8')
        response = requests.get(url, headers=headers, stream=True)
        res = Response(stream_with_context(response.iter_content(chunk_size=2048)),
                       content_type=response.headers['Content-Type'],
                       headers=headers)

        res.headers['Accept-Ranges'] = 'bytes'
        res.headers['Content-Length'] = response.headers['Content-Length']
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            res.headers['Content-Disposition'] = content_disposition
        return res
    except Exception as e:
        logger.exception(f'forward error: {e}')
        return str(e), 400

def run_server(port):
    app.run(host='127.0.0.1', port=port)

def run_server_multiprocess(port):
    process = multiprocessing.Process(target=run_server, args=(port,))
    process.start()
