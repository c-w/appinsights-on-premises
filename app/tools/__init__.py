from urllib.parse import ParseResult

import wait


def wait_for(url: ParseResult):
    wait.tcp.open(url.port or 80, url.hostname or 'localhost')
