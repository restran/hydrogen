import logging
from threading import Thread, Lock
from time import sleep

import webview
import settings

# 通过这种方式运行，DEBUG 不能为
settings.DEBUG = False

from server import run_server

server_lock = Lock()

logger = logging.getLogger(__name__)


def url_ok(url, port):
    # Use httplib on Python 2
    try:
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection

    try:
        conn = HTTPConnection(url, port)
        conn.request("GET", "/")
        r = conn.getresponse()
        return r.status == 200
    except:
        logger.exception("Server not started")
        return False


if __name__ == '__main__':
    logger.debug("Starting server")
    t = Thread(target=run_server)
    t.daemon = True
    t.start()
    logger.debug("Checking server")

    while not url_ok("127.0.0.1", settings.PORT):
        sleep(0.1)

    logger.debug("Server started")
    webview.create_window(settings.APP_NAME, "http://127.0.0.1:%s" % settings.PORT, min_size=(640, 480))
