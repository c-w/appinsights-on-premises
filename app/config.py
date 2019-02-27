from collections import namedtuple
from importlib import import_module
from os import cpu_count
from os import environ
from pathlib import Path
from typing import Iterable
from typing import Optional
from urllib.parse import unquote

from furl import furl

DatabaseUrl = namedtuple('DatabaseUrl', (
    'host',
    'options',
    'password',
    'path',
    'port',
    'scheme',
    'username',
    'raw',
))


# noinspection PyPep8Naming
class _Config:
    def __init__(self, env: Optional[dict] = None):
        self._env = dict(env or environ)

    @property
    def DEBUG(self) -> bool:
        return self._env.get('DEBUG') == 'True'

    @property
    def HOST(self) -> str:
        return self._env.get('HOST', '127.0.0.1')

    @property
    def PORT(self) -> int:
        return int(self._env.get('PORT', '8000'))

    @property
    def WORKERS(self) -> int:
        return int(self._env.get('WORKERS', str(cpu_count())))

    @property
    def DATABASE_URL(self) -> DatabaseUrl:
        url = furl(self._env.get('DATABASE_URL', ''))
        return DatabaseUrl(
            host=url.host,
            options=dict(url.args),
            password=unquote(url.password) if url.password else None,
            path=str(url.path),
            port=url.port,
            scheme=url.scheme,
            username=url.username,
            raw=str(url))

    @property
    def DATABASE(self):
        module = 'app.database.{}'.format(self.DATABASE_URL.scheme)
        return import_module(module)

    @property
    def DATABASE_INIT(self) -> Iterable[Path]:
        for path in self._env.get('DATABASE_INIT', '').split(';'):
            path = Path(path)
            if path.is_file():
                yield path

    def update(self, values: dict):
        for key, value in values.items():
            if key and value and hasattr(self, key.upper()):
                self._env[key.upper()] = str(value)


config = _Config()
