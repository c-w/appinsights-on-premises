import gzip
import json

from sanic import Sanic
from sanic import response
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_cors import CORS

from app.config import config
from app.domain.exceptions import UnknownClient

app = Sanic(__name__)
CORS(app, automatic_options=True)


@app.middleware
async def decompress_request(request):
    if request.headers.get('content-encoding') == 'gzip':
        request.body = gzip.decompress(request.body)


@app.route('/', methods=['POST'])
async def ingest(request: Request) -> HTTPResponse:
    content_type = request.headers.get('content-type')

    if 'application/json' in content_type:
        telemetries = request.json
    elif 'application/x-json-stream' in content_type:
        telemetries = [json.loads(line) for line in request.body.split(b'\n')]
    else:
        return response.json({'error': 'unknown content-type'}, status=400)

    try:
        await config.DATABASE.ingest(telemetries)
    except UnknownClient:
        return response.json({'error': 'unknown client'}, status=403)
    except NotImplementedError:
        return response.json({'error': 'unknown telemetry'}, status=500)

    return response.json({'ingested': len(telemetries)})
