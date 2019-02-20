"""Script to boostrap the telemetry server start process"""
from os import getenv
from subprocess import check_call
from sys import executable
from typing import Optional

from app.tools.run_server import main as run_server


def main(ikey: Optional[str] = None):
    check_call([executable, '-m', 'app.tools.create_db'])

    ikey = ikey or getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
    if ikey:
        check_call([executable, '-m', 'app.tools.register_client', '--ikey', ikey])

    run_server()


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--ikey')
    args = parser.parse_args()

    main(args.ikey)


if __name__ == '__main__':
    cli()
