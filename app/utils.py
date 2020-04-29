import socket
import time


def wait_for_port(host, port, sleep=1, retries=300):
    for _ in range(retries):
        try:
            sock = socket.create_connection((host, port))
            sock.close()
        except Exception:
            time.sleep(sleep)
