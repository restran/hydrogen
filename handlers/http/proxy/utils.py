# -*- coding: utf-8 -*-
# Created by restran on 2018/5/29
from __future__ import unicode_literals, absolute_import

import errno
import os
import ssl
import time
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509.oid import NameOID
from mountains import logging
from tornado import ioloop

from settings import get_path

logger = logging.getLogger(__name__)


class FileLockTimeoutException(Exception):
    pass


class FileLock(object):
    """
    Based on http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/
    """

    def __init__(self, file_name, timeout=30, delay=.15):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        self.is_locked = False
        self.lockfile = os.path.join(os.getcwd(), '%s.lock' % file_name)
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay

    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws
            an exception.
        """
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self.timeout:
                    raise FileLockTimeoutException('%d seconds passed.' % self.timeout)
                time.sleep(self.delay)
        self.is_locked = True

    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            self.is_locked = False

    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):  # @UnusedVariable
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        self.release()


def gen_signed_cert(domain):
    """
    This function takes a domain name as a parameter and then creates a certificate and key with the
    domain name(replacing dots by underscores), finally signing the certificate using specified CA and
    returns the path of key and cert files. If you are yet to generate a CA then check the top comments
    """
    ca_crt = os.path.join(get_path('ca'), 'ca.crt')
    ca_key = os.path.join(get_path('ca'), 'ca.key')
    key_path = os.path.join(get_path('ca'), 'cert.key')
    certs_folder = get_path('certs')

    cert_path = os.path.join(certs_folder, domain.replace('.', '_').replace('*', '_') + '.crt')
    if os.path.exists(key_path) and os.path.exists(cert_path):
        return key_path, cert_path

    # Check happens if the certificate and key pair already exists for a domain
    if os.path.exists(key_path) and os.path.exists(cert_path):
        pass
    else:
        with FileLock(cert_path, timeout=2):
            # Check happens if the certificate and key pair already exists for a domain
            if os.path.exists(key_path) and os.path.exists(cert_path):
                pass
            else:
                # The CA stuff is loaded from the same folder as this script
                # ca_cert = load_pem_x509_certificate(open(ca_crt, 'rb').read(), default_backend())
                # The last parameter is the password for your CA key file
                ca_key = load_pem_private_key(open(ca_key, 'rb').read(), None, default_backend())
                key = load_pem_private_key(open(key_path, 'rb').read(), None, default_backend())

                # key.generate_key(crypto.TYPE_RSA, 2048)
                subject = issuer = x509.Name([
                    x509.NameAttribute(NameOID.COUNTRY_NAME, 'US'),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'CA'),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, 'San Francisco'),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Hydrogen"),
                    x509.NameAttribute(NameOID.COMMON_NAME, domain),
                ])

                cert = x509.CertificateBuilder().subject_name(
                    subject
                ).issuer_name(
                    issuer
                ).public_key(
                    key.public_key()
                ).serial_number(
                    x509.random_serial_number()
                ).not_valid_before(
                    datetime.utcnow()
                ).not_valid_after(
                    # Our certificate will be valid for 365 * 2 days
                    datetime.utcnow() + timedelta(days=365 * 2)
                ).add_extension(
                    x509.SubjectAlternativeName([x509.DNSName(domain)]),
                    critical=False,
                    # Sign our certificate with our private key
                ).sign(ca_key, hashes.SHA256(), default_backend())
                # Write our certificate out to disk.
                # The key and cert files are dumped and their paths are returned
                domain_cert = open(cert_path, 'wb')
                cert.public_bytes(serialization.Encoding.PEM)
                domain_cert.write(cert.public_bytes(serialization.Encoding.PEM))
                logger.warning(("[*] Generated signed certificate for %s" % domain))
    return key_path, cert_path


def wrap_socket(socket, domain, success=None, failure=None, io=None, **options):
    """Wrap an active socket in an SSL socket."""

    # # Default Options
    options.setdefault('do_handshake_on_connect', False)
    options.setdefault('ssl_version', ssl.PROTOCOL_SSLv23)
    options.setdefault('server_side', True)

    # The idea is to handle domains with greater than 3 dots using wildcard certs
    if domain.count(".") >= 3:
        key, cert = gen_signed_cert('*.' + '.'.join(domain.split('.')[-3:]))
    else:
        key, cert = gen_signed_cert(domain)
    options.setdefault('certfile', cert)
    options.setdefault('keyfile', key)

    # Handlers
    def done():
        """Handshake finished successfully."""
        io.remove_handler(wrapped.fileno())
        if success:
            success(wrapped)

    def error():
        """The handshake failed."""

        if failure:
            return failure(wrapped)
        # # By default, just close the socket.
        io.remove_handler(wrapped.fileno())
        wrapped.close()

    def handshake(fd, events):
        """Handler fGetting the same error here... also looking for answers....
        TheHippo Dec 19 '12 at 20:29or SSL handshake negotiation.
        See Python docs for ssl.do_handshake()."""

        if events & io.ERROR:
            error()
            return
        new_state = io.ERROR
        try:
            wrapped.do_handshake()
            return done()
        except ssl.SSLError as exc:
            if exc.args[0] == ssl.SSL_ERROR_WANT_READ:
                new_state |= io.READ
            elif exc.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                new_state |= io.WRITE
            else:
                raise
        except Exception as e:
            logger.error(e)

        if new_state != state[0]:
            state[0] = new_state
            io.update_handler(fd, new_state)

    # # set up handshake state; use a list as a mutable cell.
    io = io or ioloop.IOLoop.instance()
    state = [io.ERROR]

    # Wrap the socket; swap out handlers.
    io.remove_handler(socket.fileno())
    wrapped = ssl.SSLSocket(socket, **options)
    wrapped.setblocking(0)
    io.add_handler(wrapped.fileno(), handshake, state[0])

    # Begin the handshake.
    handshake(wrapped.fileno(), 0)
    return wrapped


def headers_2_str(headers):
    result = []
    for k, v in headers.items():
        result.append('%s: %s' % (k, v))

    return '\n'.join(result)
