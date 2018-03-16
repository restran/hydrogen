# -*- coding: utf-8 -*-
# Created by restran on 2017/7/17
from __future__ import unicode_literals, absolute_import

import os

from bottle import Bottle, run
from bottle import static_file
from mountains import logging
from mountains.logging import StreamHandler, RotatingFileHandler

import settings
from urls import init_url_rules

if settings.DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO

logging.init_log(StreamHandler(level=level),
                 RotatingFileHandler(level=level, max_bytes=1024 * 1024 * 3, backup_count=1),
                 disable_existing_loggers=True)
logger = logging.getLogger(__name__)


def get_path(target_path):
    path = os.path.join(os.getcwd(), target_path)  # development path
    if not os.path.exists(path):  # frozen executable path
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), target_path)

    logger.info(path)
    return path


# 静态文件目录，要用这个格式配置，不然会找不到
app = Bottle()


@app.route('/static/<path:path>')
def callback(path):
    return static_file(path, get_path('static'))


@app.route("/")
def landing():
    # 不能用 send_from_directory，不然打包成 exe 后找不到文件
    return static_file('index.html', get_path('templates'))


@app.error(500)
def error404(e):
    return '500 %s' % e


@app.error(404)
def error404(e):
    return '404 %s ' % e


def run_server():
    init_url_rules(app)
    run(app, host='127.0.0.1', port=settings.PORT, debug=False)
    # app.run(host="127.0.0.1", port=settings.PORT, threaded=True)


if __name__ == "__main__":
    run_server()
