# -*- coding: utf-8 -*-
# Created by restran on 2017/7/17
from __future__ import unicode_literals, absolute_import

import pycurl

import records
import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from mountains import logging
from mountains.logging import StreamHandler, RotatingFileHandler

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
logging.getLogger('tornado.curl_httpclient').disabled = True
logging.getLogger('tornado.general').disabled = True

logger = logging.getLogger(__name__)

logger.info('%s' % pycurl.version)

SQL_CREATE_TABLE_INTERCEPTOR = """
CREATE TABLE "interceptor" (
"uuid"  TEXT NOT NULL,
"code"  TEXT,
"create_date"  TEXT,
"name"  TEXT,
PRIMARY KEY ("uuid" ASC)
)"""

SQL_CREATE_TABLE_HTTP_HISTORY = """
CREATE TABLE "http_history" (
"uuid"  TEXT NOT NULL,
"url"  TEXT,
"request_date"  TEXT,
"request_headers"  TEXT,
"response_headers"  TEXT,
"status_code"  INTEGER,
"elapsed"  INTEGER,
"extra_data"  TEXT,
"method"  TEXT,
"request_body"  TEXT,
"response_body"  TEXT,
PRIMARY KEY ("uuid" ASC)
)"""

SQL_CREATE_INDEX_HTTP_HISTORY = [
    """CREATE INDEX "main"."http_history_date" ON "http_history" ("request_date" ASC)""",
    """CREATE UNIQUE INDEX "main"."http_uuid" ON "http_history" ("uuid" ASC)"""
]


class Application(tornado.web.Application):
    def __init__(self):
        tornado_settings = dict(
            debug=False,
            static_path=get_path('static'),
        )
        self.database = records.Database('sqlite:///database.db')
        tornado.web.Application.__init__(self, url_handlers, **tornado_settings)

        sql = "select name from sqlite_master where type='table' order by name"
        rows = self.database.query(sql).as_dict()
        name_set = set([t['name'] for t in rows])
        if 'interceptor' not in name_set:
            self.database.query(SQL_CREATE_TABLE_INTERCEPTOR)

        if 'http_history' not in name_set:
            self.database.query(SQL_CREATE_TABLE_HTTP_HISTORY)
            for t in SQL_CREATE_INDEX_HTTP_HISTORY:
                self.database.query(t)


def run_server():
    # 为了能在线程中启动 tornado 的 event_loop
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(settings.PORT, settings.HOST)
    logger.info('hydrogen server is running on %s:%s' % (settings.HOST, settings.PORT))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run_server()
