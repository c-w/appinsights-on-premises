from datetime import timedelta
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import Union
from uuid import uuid4

from async_lru import alru_cache
from asyncpg import Connection
from asyncpg import ForeignKeyViolationError
from asyncpg import UniqueViolationError
from asyncpg import create_pool
from asyncpg.pool import Pool
from dateutil.parser import parse
from ujson import dumps

from app.config import config
from app.domain.appinsights import APPINSIGHTS_EVENT
from app.domain.appinsights import APPINSIGHTS_EXCEPTION
from app.domain.appinsights import APPINSIGHTS_LOG
from app.domain.appinsights import APPINSIGHTS_REQUEST
from app.domain.exceptions import DuplicateClient
from app.domain.exceptions import UnknownClient

Database = Union[Connection, Pool]


@alru_cache(maxsize=1)
async def _get_db_pool() -> Pool:
    return await create_pool(
        min_size=int(config.DATABASE_OPTIONS.get('pool_min_size') or '1'),
        max_size=int(config.DATABASE_OPTIONS.get('pool_max_size') or '2'),
        database=config.DATABASE_URL.path[1:],
        user=config.DATABASE_URL.username,
        password=config.DATABASE_URL.password,
        host=config.DATABASE_URL.hostname,
        port=config.DATABASE_URL.port,
        ssl=config.DATABASE_OPTIONS.get('ssl') == 'True',
    )


def _nullsafe(converter, data):
    return converter(data) if data is not None else None


def _to_interval(interval: str) -> timedelta:
    """
    >>> _to_interval('00:00:00.223').total_seconds()
    0.223
    >>> _to_interval('01:02:03.40').total_seconds()
    3723.04
    """
    rest, milliseconds = interval.split('.')
    hours, minutes, seconds = rest.split(':')
    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(milliseconds),
    )


async def _insert_events(db: Database, telemetries: Iterable[dict]):
    await db.executemany('''
        INSERT INTO events (
            client,
            created_at,
            name,
            properties,
            _original
        ) VALUES (
            $1::UUID,
            $2,
            $3,
            $4,
            $5
        )
    ''', [(
        telemetry['iKey'],
        parse(telemetry['time']),
        telemetry['data']['baseData']['name'],
        dumps(telemetry['data']['baseData'].get('properties', {})),
        dumps(telemetry)
    ) for telemetry in telemetries])


async def _insert_logs(db: Database, telemetries: Iterable[dict]):
    await db.executemany('''
        INSERT INTO logs (
            client,
            created_at,
            message,
            severity,
            _original
        ) VALUES (
            $1::UUID,
            $2,
            $3,
            $4,
            $5
        )
    ''', [(
        telemetry['iKey'],
        parse(telemetry['time']),
        telemetry['data']['baseData']['message'],
        telemetry['data']['baseData']['severityLevel'],
        dumps(telemetry)
    ) for telemetry in telemetries])


async def _insert_exceptions(db: Database, telemetries: Iterable[dict]):
    await db.executemany('''
        INSERT INTO exceptions (
            client,
            created_at,
            exceptions,
            _original
        ) VALUES (
            $1::UUID,
            $2,
            $3,
            $4
        )
    ''', [(
        telemetry['iKey'],
        parse(telemetry['time']),
        dumps(telemetry['data']['baseData'].get('exceptions', [])),
        dumps(telemetry)
    ) for telemetry in telemetries])


async def _insert_requests(db: Database, requests: Iterable[dict]):
    await db.executemany('''
        INSERT INTO requests (
            client,
            created_at,
            name,
            url,
            status_code,
            success,
            duration,
            _original
        ) VALUES (
            $1::UUID,
            $2,
            $3,
            $4,
            $5,
            $6,
            $7,
            $8
        )
    ''', [(
        request['iKey'],
        parse(request['time']),
        request['data']['baseData']['name'],
        request['data']['baseData']['url'],
        _nullsafe(int, request['data']['baseData'].get('responseCode')),
        request['data']['baseData'].get('success'),
        _nullsafe(_to_interval, request['data']['baseData'].get('duration')),
        dumps(request)
    ) for request in requests])


_INSERTERS = {
    APPINSIGHTS_EVENT: _insert_events,
    APPINSIGHTS_LOG: _insert_logs,
    APPINSIGHTS_EXCEPTION: _insert_exceptions,
    APPINSIGHTS_REQUEST: _insert_requests,
}


async def create():
    db = await _get_db_pool()

    schema_file = Path(__file__).parent / 'postgres.sql'
    with schema_file.open(encoding='utf-8') as fobj:
        schema = fobj.read()

    for statement in schema.split(';'):
        if statement.strip():
            await db.execute(statement)


async def register(client: Optional[str] = None) -> str:
    client = client or str(uuid4())

    db = await _get_db_pool()

    try:
        await db.execute('INSERT INTO clients (client) VALUES ($1)', client)
    except UniqueViolationError:
        raise DuplicateClient()

    return client


async def ingest(telemetries: Iterable[dict]):
    pool = await _get_db_pool()

    async with pool.acquire() as db:
        async with db.transaction():
            try:
                for event_type, group in groupby(telemetries, itemgetter('name')):
                    try:
                        inserter = _INSERTERS[event_type]
                    except KeyError:
                        raise NotImplementedError(event_type)
                    else:
                        await inserter(db, group)
            except ForeignKeyViolationError:
                raise UnknownClient()
