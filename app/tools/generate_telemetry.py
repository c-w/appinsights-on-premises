"""Script to send random telemetry to Application Insights"""
from random import choice
from random import seed
from string import ascii_letters
from logging import getLogger

from applicationinsights import TelemetryClient
from applicationinsights.channel import SynchronousQueue
from applicationinsights.channel import SynchronousSender
from applicationinsights.channel import TelemetryChannel
from applicationinsights.channel import TelemetryContext

LOG = getLogger(__name__)


def random_string(size: int) -> str:
    return ''.join(choice(ascii_letters) for _ in range(size))


def generate_event_name(size: int = 8) -> str:
    return 'event{}'.format(random_string(size))


def generate_event_properties(size: int = 8) -> dict:
    return {
        'property{}'.format(i): random_string(size)
        for i in range(size)
    }


def generate_log_message(size: int = 128) -> str:
    return 'log{}'.format(random_string(size))


def generate_log_severity() -> str:
    return choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])


def generate_exception(size: int = 8) -> Exception:
    return Exception(random_string(size))


def main(endpoint: str, ikey: str,
         num_events: int, num_traces: int, num_exceptions: int):
    sender = SynchronousSender(endpoint)
    queue = SynchronousQueue(sender)
    context = TelemetryContext()
    context.instrumentation_key = ikey
    channel = TelemetryChannel(context, queue)
    client = TelemetryClient(ikey, telemetry_channel=channel)

    for _ in range(num_events):
        event = generate_event_name()
        properties = generate_event_properties()
        client.track_event(event, properties)
        LOG.info('sent event %s %r', event, properties)

    for _ in range(num_traces):
        trace = generate_log_message()
        severity = generate_log_severity()
        client.track_trace(trace, severity=severity)
        LOG.info('sent trace %s %d', trace, severity)

    for _ in range(num_exceptions):
        exception = generate_exception()
        try:
            raise exception
        except Exception:
            client.track_exception()
            LOG.info('sent exception %s', exception)

    client.flush()


def cli():
    from argparse import ArgumentParser
    from os import getenv

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--ikey', required=True)
    parser.add_argument('--endpoint', default=getenv('APP_URL'))
    parser.add_argument('--num_events', type=int, default=10)
    parser.add_argument('--num_traces', type=int, default=10)
    parser.add_argument('--num_exceptions', type=int, default=10)
    parser.add_argument('--random_seed', type=int, default=None)
    args = parser.parse_args()

    LOG.setLevel('DEBUG')

    if args.random_seed is not None:
        seed(args.random_seed)

    main(
        endpoint=args.endpoint,
        ikey=args.ikey,
        num_events=args.num_events,
        num_traces=args.num_traces,
        num_exceptions=args.num_exceptions,
    )


if __name__ == '__main__':
    cli()
