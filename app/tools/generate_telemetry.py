"""Script to send random telemetry to Application Insights"""
from collections import namedtuple
from datetime import datetime
from logging import getLogger
from random import choice
from random import gauss
from string import ascii_letters
from urllib.parse import urlparse

from applicationinsights import TelemetryClient
from applicationinsights.channel import SynchronousQueue
from applicationinsights.channel import SynchronousSender
from applicationinsights.channel import TelemetryChannel

from app.tools import wait_for

LOG = getLogger(__name__)

SendConfig = namedtuple('SendConfig', (
    'num_events',
    'num_traces',
    'num_exceptions',
    'num_requests',
))


class NoRetrySender(SynchronousSender):
    def send(self, data_to_send):
        super().send(data_to_send)
        if not self.did_send_all_telemetry():
            raise Exception('Unable to send all telemetry')

    def did_send_all_telemetry(self) -> bool:
        # noinspection PyProtectedMember
        return self._queue._queue.qsize() == 0


def random_string(size: int) -> str:
    return ''.join(choice(ascii_letters) for _ in range(size))


def coinflip() -> bool:
    return choice([True, False])


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


def generate_request(size: int = 8) -> dict:
    name = random_string(size)
    success = coinflip()

    url = 'http://server.com/{}'.format(name)
    if coinflip():
        url += '?foo={}'.format(random_string(size))

    return {
        'name': name,
        'url': url,
        'success': success,
        'start_time': datetime.utcnow().isoformat(),
        'duration': gauss(200 if success else 400, 50 if success else 100),
        'response_code': choice([200, 201] if success else [400, 403, 500]),
        'http_method': choice(['GET', 'POST', 'HEAD', 'DELETE']),
    }


def send_events(client: TelemetryClient, num_events: int):
    for _ in range(num_events):
        event = generate_event_name()
        properties = generate_event_properties()
        client.track_event(event, properties)
        LOG.info('sent event %s %r', event, properties)


def send_logs(client: TelemetryClient, num_traces: int):
    for _ in range(num_traces):
        trace = generate_log_message()
        severity = generate_log_severity()
        client.track_trace(trace, severity=severity)
        LOG.info('sent trace %s %d', trace, severity)


def send_exceptions(client: TelemetryClient, num_exceptions: int):
    for _ in range(num_exceptions):
        exception = generate_exception()
        # noinspection PyBroadException
        try:
            raise exception
        except Exception:
            client.track_exception()
            LOG.info('sent exception %s', exception)


def send_requests(client: TelemetryClient, num_requests: int):
    for _ in range(num_requests):
        request = generate_request()
        client.track_request(**request)
        LOG.info('sent request %r', request)


def main(endpoint: str, ikey: str, send_config: SendConfig):
    wait_for(urlparse(endpoint))

    sender = NoRetrySender(endpoint)
    queue = SynchronousQueue(sender)
    channel = TelemetryChannel(queue=queue)
    client = TelemetryClient(ikey, channel)

    send_events(client, send_config.num_events)
    send_logs(client, send_config.num_traces)
    send_exceptions(client, send_config.num_exceptions)
    send_requests(client, send_config.num_requests)

    client.flush()


def cli():
    from argparse import ArgumentParser
    from os import getenv
    from random import seed

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--ikey', required=True)
    parser.add_argument('--endpoint', default=getenv('APP_URL'))
    parser.add_argument('--num_events', type=int, default=10)
    parser.add_argument('--num_traces', type=int, default=10)
    parser.add_argument('--num_exceptions', type=int, default=10)
    parser.add_argument('--num_requests', type=int, default=10)
    parser.add_argument('--random_seed', type=int, default=None)
    args = parser.parse_args()

    LOG.setLevel('DEBUG')

    if args.random_seed is not None:
        seed(args.random_seed)

    main(args.endpoint, args.ikey, SendConfig(
        num_events=args.num_events,
        num_traces=args.num_traces,
        num_exceptions=args.num_exceptions,
        num_requests=args.num_requests,
    ))


if __name__ == '__main__':
    cli()
