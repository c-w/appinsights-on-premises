"""Script to register a client"""
from typing import IO
from typing import Optional

from app.config import config


async def main(ikey: Optional[str], outfile: IO[str]):
    client = await config.DATABASE.register(ikey)
    outfile.write(client)


def cli():
    from argparse import ArgumentParser
    from argparse import FileType
    from asyncio import get_event_loop
    from contextlib import closing
    from sys import stdout
    from urllib.parse import urlunparse

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--database_url', default=urlunparse(config.DATABASE_URL))
    parser.add_argument('--ikey')
    parser.add_argument('--outfile', type=FileType('w', encoding='utf-8'), default=stdout)
    args = parser.parse_args()

    config.update(args.__dict__)

    with closing(get_event_loop()) as loop:
        loop.run_until_complete(main(args.ikey, args.outfile))


if __name__ == '__main__':
    cli()
