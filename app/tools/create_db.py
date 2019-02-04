"""Script to run the telemetry server"""
from asyncio import get_event_loop
from contextlib import closing
from urllib.parse import urlunparse

from app.config import config


async def main():
    await config.DATABASE.create()


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--database_url', default=urlunparse(config.DATABASE_URL))
    args = parser.parse_args()

    config.update(args.__dict__)

    with closing(get_event_loop()) as loop:
        loop.run_until_complete(main())


if __name__ == '__main__':
    cli()
