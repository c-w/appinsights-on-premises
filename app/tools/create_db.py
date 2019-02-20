"""Script to run the telemetry server"""
from syncer import sync

from app.config import config


@sync
async def main():
    await config.DATABASE.create()


def cli():
    from argparse import ArgumentParser
    from urllib.parse import urlunparse

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--database_url', default=urlunparse(config.DATABASE_URL))
    args = parser.parse_args()

    config.update(args.__dict__)

    main()


if __name__ == '__main__':
    cli()
