"""Script to run the telemetry server."""
from subprocess import check_call

from sanic.worker import GunicornWorker

from app import api
from app.config import config


def _run_sanic():
    api.app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        workers=config.WORKERS,
    )


def _run_gunicorn():
    gunicorn_command = [
        'gunicorn',
        '{}:app'.format(api.__name__),
        '--bind', '{}:{}'.format(config.HOST, config.PORT),
        '--workers', '{}'.format(config.WORKERS),
        '--worker-class', '{}.{}'.format(GunicornWorker.__module__,
                                         GunicornWorker.__qualname__),
    ]

    check_call(gunicorn_command)


def main():
    if config.DEBUG:
        _run_sanic()
    else:
        _run_gunicorn()


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=config.PORT)
    parser.add_argument('--host', default=config.HOST)
    parser.add_argument('--debug', action='store_true', default=config.DEBUG)
    parser.add_argument('--workers', type=int, default=config.WORKERS)
    args = parser.parse_args()

    config.update(args.__dict__)

    main()


if __name__ == '__main__':
    cli()
