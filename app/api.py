from sanic import Sanic
from sanic import response
from sanic.request import Request
from sanic.response import HTTPResponse

from app.config import config
from app.domain.exceptions import UnknownClient

app = Sanic(__name__)


@app.route('/', methods=['POST'])
async def ingest(request: Request) -> HTTPResponse:
    telemetries = request.json or []

    try:
        await config.DATABASE.ingest(telemetries)
    except UnknownClient:
        return response.json({'error': 'unknown client'}, status=403)
    except NotImplementedError:
        return response.json({'error': 'unknown telemetry'}, status=500)

    return response.json({'ingested': len(telemetries)})
