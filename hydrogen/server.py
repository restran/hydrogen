# -*- coding: utf-8 -*-
# Created by restran on 2017/7/17
from __future__ import unicode_literals, absolute_import
import os
from flask import Flask, render_template
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
    return path


# 静态文件目录，要用这个格式配置，不然会找不到
app = Flask(__name__, static_folder=get_path('static'),
            template_folder=get_path('templates'), )
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1  # disable caching


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route("/")
def landing():
    # 不能用 send_from_directory，不如打包成 exe 后找不到文件
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return '404', 200


@app.errorhandler(500)
def server_error(e):
    return '500', 200


def run_server():
    init_url_rules(app)
    app.run(host="127.0.0.1", port=settings.PORT, threaded=True)


if __name__ == "__main__":
    run_server()
