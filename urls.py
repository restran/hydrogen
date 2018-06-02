# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

from tornado.web import RequestHandler

from handlers.converter import api as converter_api
from handlers.crypto import api as crypto_api
from handlers.http import api as http_api
from settings import get_path


class Landing(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        path = get_path('templates/index.html')
        with open(path, 'rb') as f:
            self.write(f.read())
        self.set_header('Content-Type', 'text/html')


url_handlers = [
    (r'/?', Landing),
    (r'/api/converter/convert-data/', converter_api.ConvertData),
    (r'/api/converter/what-encode/', converter_api.WhatEncode),
    (r'/api/converter/file-converter/', converter_api.FileConverter),
    (r'/api/crypto/decode-data/', crypto_api.DecodeData),
    (r'/api/crypto/rsa-from-pem-key/', crypto_api.RSAFromPEMKey),
    (r'/api/crypto/rsa-to-pem-key/', crypto_api.RSAToPEMKey),
    (r'/api/crypto/rsa-encrypt-decrypt/', crypto_api.RSAEncryptDecrypt),
    (r'/api/crypto/aes-encrypt-decrypt/', crypto_api.AESEncryptDecrypt),
    (r'/api/http/request/', http_api.HTTPRequest),
    (r'/api/http/proxy/', http_api.HTTPProxy),
    (r'/api/http/proxy-interceptor/', http_api.HTTPInterceptor),
]
