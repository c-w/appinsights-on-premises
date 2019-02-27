"""Script to run the telemetry server."""
from syncer import sync

from app.config import config


@sync
async def main():
    config.DATABASE.wait_until_ready()
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
