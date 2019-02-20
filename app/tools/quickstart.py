"""Script to boostrap the telemetry server start process"""
from subprocess import check_call
from sys import executable

from app.tools import create_db
from app.tools import register_client
from app.tools import run_server

if __name__ == '__main__':
    check_call([executable, '-m', create_db.__name__])
    check_call([executable, '-m', register_client.__name__])
    run_server.main()
