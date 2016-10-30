# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter
import http.cookiejar
import itertools
import pickle
import twisted.internet
import twisted.internet.endpoints
import twisted.web.http
import twisted.web.proxy
import urllib.parse

JSESSIONID = comsoljupyter.JSESSIONID.encode('ascii')
CSSESSIONID = comsoljupyter.CSSESSIONID.encode('ascii')

def cookie_fmt(name, value):
    return '{0}={1}'.format(name, value)

class ReverseProxyHTTPFactory(twisted.web.http.HTTPFactory):
    def __init__(self, remote_url, cookie_jar, *a, **kw):
        super().__init__(*a, **kw)

        self.remote_url = remote_url
        self.cookie_jar = cookie_jar

    def protocol(self):
        return twisted.web.http._GenericHTTPChannelProtocol(
            ReverseProxy(self.remote_url, self.cookie_jar)
        )

class ReverseProxyRequest(twisted.web.proxy.ReverseProxyRequest):
    def process(self):
        self.requestHeaders.setRawHeaders(
            b"host",
            [self.channel.host.encode('ascii')],
        )

        self._replace_comsol_cookies()

        clientFactory = self.proxyClientFactoryClass(
            self.method, self.uri, self.clientproto, self.getAllHeaders(),
            self.content.read(), self,
        )

        client_endpoint = twisted.internet.endpoints.clientFromString(
            twisted.internet.reactor,
            self.channel.client_conn_string,
        )

        client_endpoint.connect(clientFactory)

    def _replace_comsol_cookies(self):
        cookies = self.requestHeaders.getRawHeaders(b'cookie')

        if cookies is not None:
            cookies = list(x.strip() for x in itertools.chain(*[x.split(b';') for x in cookies]))
        else:
            cookies = [CSSESSIONID, JSESSIONID]

        self.requestHeaders.setRawHeaders(b'cookie', [ self._filter_comsol_cookie(x) for x in cookies ])

    def _filter_comsol_cookie(self, cookiestr):
        if CSSESSIONID in cookiestr:
            return cookie_fmt(comsoljupyter.CSSESSIONID, self.channel.CSSESSIONID.value).encode('ascii')

        if JSESSIONID in cookiestr:
            return cookie_fmt(comsoljupyter.JSESSIONID, self.channel.JSESSIONID.value).encode('ascii')

        return cookiestr

class ReverseProxy(twisted.web.proxy.ReverseProxy):
    requestFactory = ReverseProxyRequest

    def __init__(self, remote_url, cookie_jar):
        super().__init__()

        url = urllib.parse.urlparse(remote_url)
        assert url.scheme in ('https', 'http')

        if ':' in url.netloc:
            self.host, self.proto = url.netloc.split(':')
        else:
            self.host = url.netloc
            self.port = {
                'http': 80,
                'https': 443,
            }[url.scheme]

        self.proto = {
            'http': 'tcp',
            'https': 'tls',
        }[url.scheme]

        self.client_conn_string = '{0.proto}:{0.host}:{0.port}'.format(self)

        self.CSSESSIONID = comsoljupyter.search_in_cookie_jar(
            cookie_jar,
            comsoljupyter.CSSESSIONID
        )

        self.JSESSIONID = comsoljupyter.search_in_cookie_jar(
            cookie_jar,
            comsoljupyter.JSESSIONID
        )

        assert self.CSSESSIONID is not None and self.JSESSIONID is not None

class ComsolProxy(object):
    def __init__(self, listen_port, remote_url, cookie_path):
        self.listen_port = listen_port
        self.remote_url = remote_url
        with open(cookie_path, 'br') as f:
            self.cookie_jar = pickle.load(f)

    def listen(self):
        twisted.internet.reactor.listenTCP(
            self.listen_port,
            ReverseProxyHTTPFactory(self.remote_url, self.cookie_jar),
        )
