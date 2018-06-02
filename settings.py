# -*- coding: utf-8 -*-
# Created by restran on 2017/10/12
from __future__ import unicode_literals, absolute_import

import os

APP_NAME = 'Hydrogen'
VERSION = '0.5.0'

DEBUG = True
HOST = '127.0.0.1'
PORT = 8000

PRODUCT_PORT = 23498

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_BASE_PATH = os.path.join(os.getcwd(), 'database.db')


def get_path(target_path):
    path = os.path.join(os.getcwd(), target_path)  # development path
    if not os.path.exists(path):  # frozen executable path
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), target_path)

    return path
