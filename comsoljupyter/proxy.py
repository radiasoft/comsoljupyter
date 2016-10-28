# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter.twproxy
import twisted.internet
import twisted.web.http

class ComsolProxy(object):
    def __init__(self, listen_port, remote_url):
        self.listen_port = listen_port
        self.remote_url = remote_url

    def listen(self):
        twisted.internet.reactor.listenTCP(
            self.listen_port,
            comsoljupyter.twproxy.ReverseProxyHTTPFactory(self.remote_url),
        )
