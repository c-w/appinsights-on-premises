"""
Database backend that uses Apache Libcloud to store the telemetry.

This provides support for a wide variety of object storage systems, including:
  - Azure Blob Storage
  - AWS S3
  - The filesystem

The DATABASE_URL is in the format:

    libcloud://<key>:<secret>@<provider>

"""
from functools import lru_cache
from io import BytesIO
from json import dumps
from typing import Iterable
from typing import Optional
from uuid import uuid4

import wait
from dateutil.parser import parse
from libcloud.storage.base import StorageDriver
from libcloud.storage.providers import get_driver
from libcloud.storage.types import ContainerAlreadyExistsError
from libcloud.storage.types import ContainerDoesNotExistError
from libcloud.storage.types import Provider

from app.config import config
from app.domain.exceptions import DuplicateClient
from app.domain.exceptions import UnknownClient


def _get_driver_kwargs():
    return {
        'key': config.DATABASE_URL.username,
        'secret': config.DATABASE_URL.password,
        'host': config.DATABASE_URL.options.get('endpoint') or None,
        'secure': config.DATABASE_URL.options.get('ssl') != 'False',
    }


@lru_cache(maxsize=1)
def _get_driver() -> StorageDriver:
    provider = getattr(Provider, config.DATABASE_URL.host.upper())
    driver_class = get_driver(provider)
    driver_kwargs = _get_driver_kwargs()
    return driver_class(**driver_kwargs)


def _client_to_container_name(client: str) -> str:
    return client.replace('-', '')


async def create():
    pass


async def register(client: Optional[str] = None) -> str:
    client = _client_to_container_name(client or str(uuid4()))

    storage = _get_driver()

    try:
        storage.create_container(client)
    except ContainerAlreadyExistsError:
        raise DuplicateClient()

    return client


async def ingest(telemetries: Iterable[dict]):
    telemetries = list(telemetries)
    storage = _get_driver()

    containers = []
    for telemetry in telemetries:
        client = _client_to_container_name(telemetry['iKey'])
        try:
            container = storage.get_container(client)
        except ContainerDoesNotExistError:
            raise UnknownClient()
        else:
            containers.append(container)

    for container, telemetry in zip(containers, telemetries):
        container.upload_object_via_stream(
            BytesIO(dumps(telemetry).encode('utf-8')),
            object_name='{folder}/{prefix}/{name}.json'.format(
                folder=telemetry['name'],
                prefix=parse(telemetry['time']).strftime(
                    '%Y/%m/%d/%H/%M'),
                name=str(uuid4())))


def wait_until_ready():
    driver_kwargs = _get_driver_kwargs()
    custom_host = driver_kwargs.get('host', '')
    if not custom_host:
        return

    parts = custom_host.split(':')
    if len(parts) == 1:
        host = parts[0]
        port = 443 if driver_kwargs.get('secure', True) else 80
    elif len(parts) == 2:
        host, port = parts
        port = int(port)
    else:
        raise ValueError(custom_host)

    wait.tcp.open(port, host)
