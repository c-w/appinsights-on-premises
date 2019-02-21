"""Script to boostrap the telemetry server start process"""
from os import getenv
from subprocess import check_call
from sys import executable

from app.tools import create_db
from app.tools import register_client
from app.tools import run_server

if __name__ == '__main__':
    check_call([executable, '-m', create_db.__name__])

    ikey = getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
    if ikey:
        check_call([executable, '-m', register_client.__name__, '--ikey', ikey])

    run_server.main()
