"""Script to register a client"""
from typing import IO
from typing import Optional

from syncer import sync

from app.config import config
from app.domain.exceptions import DuplicateClient
from app.tools import wait_for


@sync
async def main(ikey: Optional[str], outfile: IO[str]):
    wait_for(config.DATABASE_URL)
    try:
        client = await config.DATABASE.register(ikey)
    except DuplicateClient:
        pass
    else:
        if not ikey:
            outfile.write(client)


def cli():
    from argparse import ArgumentParser
    from argparse import FileType
    from sys import stdout
    from urllib.parse import urlunparse

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--database_url', default=urlunparse(config.DATABASE_URL))
    parser.add_argument('--ikey')
    parser.add_argument('--outfile', type=FileType('w', encoding='utf-8'), default=stdout)
    args = parser.parse_args()

    config.update(args.__dict__)

    main(args.ikey, args.outfile)


if __name__ == '__main__':
    cli()
