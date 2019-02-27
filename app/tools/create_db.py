"""Script to run the telemetry server"""
from syncer import sync

from app.config import config
from app.tools import wait_for


@sync
async def main():
    wait_for(config.DATABASE_URL)
    await config.DATABASE.create()


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--database_url', default=config.DATABASE_URL.raw)
    args = parser.parse_args()

    config.update(args.__dict__)

    main()


if __name__ == '__main__':
    cli()
