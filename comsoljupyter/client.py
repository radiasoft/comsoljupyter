# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from http import HTTPStatus
from pykern import pkdebug
from twisted.internet import defer
import html.parser
import http.cookiejar
import io
import twisted.internet
import twisted.web.client
import twisted.web.http_headers
import urllib.parse

CSSESSIONID = 'CSSESSIONID'
JSESSIONID = 'JSESSIONID'

class ComsolClientError(Exception): pass

class HTMLTitleParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = False
        self.title_data = None

    def handle_data(self, data):
        if self.title:
            pkdebug.pkdc(data)
            self.title_data = data

    def handle_endtag(self, tag):
        if tag == 'title':
            self.title = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.title = True


class ComsolClient(object):
    _login_title = 'Log in to COMSOL Server'
    _library_title = 'Application Library | COMSOL Server'
    _j_security_check = 'j_security_check'
    _app_lib = 'app-lib'
    def __init__(self, base_url, user, password, cookie_jar=None):
        self._cookie_cache = {}
        self.base_url = base_url
        self.cookie_jar = http.cookiejar.MozillaCookieJar() if cookie_jar is None else cookie_jar
        self.password = password
        self.user = user

        agent = twisted.web.client.Agent(twisted.internet.reactor)
        browser_agent = twisted.web.client.BrowserLikeRedirectAgent(agent)
        self.agent = twisted.web.client.CookieAgent(browser_agent, self.cookie_jar)

    def _url(self, path):
        return urllib.parse.urljoin(self.base_url, path)

    @staticmethod
    def check_response(resp, expected):
        if resp.code != expected:
            msg = "Response {0.phrase} ({0.code}), expected {1.phrase} ({1.value})"\
                            .format(resp, expected)
            raise ComsolClientError(msg)

    @property
    def CSSESSIONID(self):
        return self.get_cookie(CSSESSIONID)

    def get(self, path, headers={}, *a, **kw):
        url = self._url(path)
        pkdebug.pkdc('GET {}', url)
        return self.agent.request(
            headers=twisted.web.http_headers.Headers(headers),
            method=b'GET',
            uri=url.encode(),
            *a,
            **kw,
        )

    def get_cookie(self, name):
        if name not in self._cookie_cache:
            for cookie in self.cookie_jar:
                if cookie.name == name:
                    self._cookie_cache[name] = cookie
                    break
        return self._cookie_cache.get(name, None)

    @property
    def has_session(self):
        return self.CSSESSIONID is not None and self.JSESSIONID is not None

    @property
    def JSESSIONID(self):
        return self.get_cookie(JSESSIONID)

    def login(self):
        def handle_login_resp(resp):
            self.check_response(resp, HTTPStatus.OK)
            pkdebug.pkdc('{}', resp.headers)
            pkdebug.pkdc('{}', self.cookie_jar)

            return self.has_session

        def do_login(resp):
            self.check_response(resp, HTTPStatus.OK)
            pkdebug.pkdc('{}', resp.headers)
            pkdebug.pkdc('{}', self.cookie_jar)

            return self.post_form(
                form_values={'j_username': self.user, 'j_password': self.password},
                path=self._j_security_check,
            ).addCallback(handle_login_resp)

        # Do a request to get Cookies stored in the client
        # if successful, execute a login request
        return self.get(self._app_lib).addCallback(do_login)

    def post(self, path, headers={}, *a, **kw):
        url = self._url(path)
        pkdebug.pkdc('POST {}', url)
        return self.agent.request(
            headers=twisted.web.http_headers.Headers(headers),
            method=b'POST',
            uri=url.encode(),
            *a,
            **kw,
        )

    def post_form(self, path, form_values):
        data = urllib.parse.urlencode(form_values)
        return self.post(
            bodyProducer=twisted.web.client.FileBodyProducer(io.BytesIO(data.encode())),
            headers={'Content-Type': ['application/x-www-form-urlencoded']},
            path=path,
        )

    def session_active(self):
        if not self.has_session:
            d = defer.Deferred()
            d.callback(False)
            return d

        def handle_body(body):
            parser = HTMLTitleParser()
            parser.feed(body.decode('utf-8'))

            if parser.title_data == self._library_title:
                return True
            return False

        def handle_resp(resp):
            self.check_response(resp, HTTPStatus.OK)
            pkdebug.pkdc('{}', resp.headers)
            pkdebug.pkdc('{}', self.cookie_jar)
            return twisted.web.client.readBody(resp).addCallback(handle_body)

        return self.get(self._app_lib).addCallback(handle_resp)

