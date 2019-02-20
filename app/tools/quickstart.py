"""Script to boostrap the telemetry server start process"""
from io import StringIO
from os import getenv
from typing import Optional

from app.tools.create_db import main as create_db
from app.tools.register_client import main as register_client
from app.tools.run_server import main as run_server


def main(ikey: Optional[str] = None):
    create_db()

    ikey = ikey or getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
    if ikey:
        register_client(ikey, StringIO())

    run_server()


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--ikey')
    args = parser.parse_args()

    main(args.ikey)


if __name__ == '__main__':
    cli()
