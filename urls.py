# -*- coding: utf-8 -*-
# Created by restran on 2017/10/13
from __future__ import unicode_literals, absolute_import

from bottle import Bottle

from handlers.converter import api as converter_api
from handlers.crypto import api as crypto_api
from handlers.http import api as http_api

url_handlers = [
    ('/api/converter/convert-data/', converter_api.convert_data, ['POST']),
    ('/api/converter/what-encode/', converter_api.what_encode, ['POST']),
    ('/api/crypto/decode-data/', crypto_api.decode_data, ['POST']),
    ('/api/crypto/rsa-from-pem-key/', crypto_api.rsa_from_pem_key, ['POST']),
    ('/api/crypto/rsa-to-pem-key/', crypto_api.rsa_to_pem_key, ['POST']),
    ('/api/crypto/rsa-encrypt-decrypt/', crypto_api.rsa_encrypt_decrypt, ['POST']),
    ('/api/crypto/aes-encrypt-decrypt/', crypto_api.aes_encrypt_decrypt, ['POST']),
    ('/api/http/request/', http_api.http_request, ['POST']),
    ('/api/http/proxy/', http_api.http_proxy, ['POST'])
    ('/api/http/proxy-interceptor/', http_api.http_interceptor, ['POST'])
]


def init_url_rules(app: Bottle, url_map_list=url_handlers):
    for u in url_map_list:
        if len(u) > 2:
            methods = u[2]
        else:
            methods = None

        app.route(path=u[0], method=methods, callback=u[1])
