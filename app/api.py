from sanic import Sanic
from sanic import response
from sanic.request import Request
from sanic.response import HTTPResponse

from app.config import config
from app.domain.exceptions import DuplicateClient
from app.domain.exceptions import UnknownClient

app = Sanic(__name__)


@app.route('/register', methods=['POST'])
async def register(request: Request) -> HTTPResponse:
    ikey = (request.json or {}).get('ikey')

    try:
        client = await config.DATABASE.register(ikey)
    except DuplicateClient:
        return response.json({'error': 'client already exists'}, status=409)

    return response.json({'ikey': client})


@app.route('/', methods=['POST'])
async def ingest(request: Request) -> HTTPResponse:
    telemetries = request.json or []

    try:
        await config.DATABASE.ingest(telemetries)
    except UnknownClient:
        return response.json({'error': 'unknown client'}, status=403)
    except NotImplementedError:
        return response.json({'error': 'unknown telemetry'}, status=400)

    return response.json({'ingested': len(telemetries)})
