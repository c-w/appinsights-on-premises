from importlib import import_module
from os import cpu_count
from os import environ
from urllib.parse import ParseResult
from urllib.parse import parse_qs
from urllib.parse import urlparse


# noinspection PyPep8Naming
class _Config:
    def __init__(self, env: dict = environ):
        self._env = dict(env)

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
    def DATABASE_URL(self) -> ParseResult:
        return urlparse(self._env.get('DATABASE_URL'))

    @property
    def DATABASE_OPTIONS(self) -> dict:
        return {
            key: values[0] if values else None
            for key, values in parse_qs(self.DATABASE_URL.query).items()
        }

    @property
    def DATABASE(self):
        module = 'app.database.{}'.format(self.DATABASE_URL.scheme)
        return import_module(module)

    def update(self, values: dict):
        for key, value in values.items():
            if key and value:
                self._env[key.upper()] = str(value)


config = _Config()
