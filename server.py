# -*- coding: utf-8 -*-
# Created by restran on 2017/7/17
from __future__ import unicode_literals, absolute_import

import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options

import tornado.web
from bottle import Bottle
from bottle import static_file
from mountains import logging
from mountains.logging import StreamHandler, RotatingFileHandler
from tornado.options import options
import records

import settings
from settings import get_path
from urls import url_handlers

if settings.DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO

logging.init_log(StreamHandler(level=level),
                 RotatingFileHandler(level=level, max_bytes=1024 * 1024 * 3, backup_count=1),
                 disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = Bottle()


# 静态文件目录，要用这个格式配置，不然会找不到
@app.route('/static/<path:path>')
def callback(path):
    return static_file(path, get_path('static'))


@app.route("/")
def landing():
    # 不能用 send_from_directory，不然打包成 exe 后找不到文件
    return static_file('index.html', get_path('templates'))


# @app.error(500)
# def error404(e):
#     return '500 %s' % e
#
#
# @app.error(404)
# def error404(e):
#     return '404 %s ' % e


class Application(tornado.web.Application):
    def __init__(self):
        tornado_settings = dict(
            debug=False,
            static_path=get_path('static'),
        )
        self.database = records.Database('sqlite:///database.db')
        tornado.web.Application.__init__(self, url_handlers, **tornado_settings)


app = Application()


def run_server():
    # 为了能在线程中启动 tornado 的 event_loop
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(settings.PORT, settings.HOST)
    logger.info('hydrogen server is running on %s:%s' % (settings.HOST, settings.PORT))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run_server()
