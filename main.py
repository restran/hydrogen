# -*- coding: utf-8 -*-
# Created by restran on 2017/7/17
from __future__ import unicode_literals, absolute_import

import logging
from threading import Thread
from time import sleep

import requests
import webview

import settings
from utils import is_port_open

logger = logging.getLogger(__name__)

# 通过这种方式运行，DEBUG 不能为 True
settings.DEBUG = False
settings.PORT = settings.PRODUCT_PORT

while is_port_open('127.0.0.1', settings.PORT):
    logger.info('port %s is unavailable' % settings.PORT)
    settings.PORT += 1


def url_ok(url):
    try:
        return requests.get(url, timeout=3).status_code == 200
    except Exception as e:
        logger.error("Server not started, %s" % e)
        return False


def main():
    logger.info("Starting server")
    from server import run_server

    t = Thread(target=run_server)
    t.daemon = True
    t.start()

    max_count = 50
    logger.info("Checking server")
    while not url_ok("http://127.0.0.1:%s/" % settings.PORT) and max_count > 0:
        sleep(0.1)
        max_count -= 1
        logger.info('sleep...')

    logger.info("Server started in 127.0.0.1:%s" % settings.PORT)
    webview.create_window(settings.APP_NAME, "http://127.0.0.1:%s" % settings.PORT, min_size=(640, 480))


if __name__ == '__main__':
    main()
