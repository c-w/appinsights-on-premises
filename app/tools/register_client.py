"""Script to register a client"""
from typing import IO

import requests


def main(base_url: str, outfile: IO[str], ikey: str):
    endpoint = base_url.rstrip('/') + '/register'
    response = requests.post(endpoint, json={'ikey': ikey} if ikey else None)
    response.raise_for_status()
    outfile.write(response.json()['ikey'])


def cli():
    from argparse import ArgumentParser
    from argparse import FileType
    from os import getenv
    from sys import stdout

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--base_url', default=getenv('APP_URL'))
    parser.add_argument('--ikey')
    parser.add_argument('--outfile', type=FileType('w', encoding='utf-8'), default=stdout)
    args = parser.parse_args()

    main(
        base_url=args.base_url,
        outfile=args.outfile,
        ikey=args.ikey,
    )


if __name__ == '__main__':
    cli()
