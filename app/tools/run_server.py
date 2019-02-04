"""Script to run the telemetry server"""
from app.config import config
from app.api import app


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=config.PORT)
    parser.add_argument('--host', default=config.HOST)
    parser.add_argument('--debug', action='store_true', default=config.DEBUG)
    parser.add_argument('--workers', type=int, default=config.WORKERS)
    args = parser.parse_args()

    config.update(args.__dict__)

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        workers=config.WORKERS,
    )


if __name__ == '__main__':
    cli()
