from furl import furl
import wait


def wait_for(url: furl):
    wait.tcp.open(url.port, url.host)
