# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from twisted.internet import reactor
import comsoljupyter.proxy

def default_command(listen_port, host_url, cookie_path):
    proxy = comsoljupyter.proxy.ComsolProxy(listen_port, host_url, cookie_path)
    proxy.listen()
    reactor.run()
