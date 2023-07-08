import base64
import json
import multiprocessing

import requests
from flask import Flask, Response, request, stream_with_context
from music_service.utils import get_logger, USER_AGENT

logger = get_logger('BridgeServer')
app = Flask(__name__)

default_headers = {
    'User-Agent': USER_AGENT
}

@app.route('/forward', methods=['GET'])
def forward():
    base64_url = request.args.get('url')
    base64_headers = request.args.get('headers')
    if not base64_url:
        return 'Invalid arguments', 400

    request_headers = default_headers.copy()
    if base64_headers:
        try:
            request_headers.update(json.loads(base64.b64decode(base64_headers)))
        except Exception as e:
            logger.exception(f'compose request headers error: {e}')

    try:
        url = base64.b64decode(base64_url).decode('utf-8')
        response = requests.get(url, headers=request_headers, stream=True)
        res = Response(stream_with_context(response.iter_content(chunk_size=2048)),
                       content_type=response.headers['Content-Type'])

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
