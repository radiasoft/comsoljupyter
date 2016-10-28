# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from twisted.internet import reactor
import comsoljupyter.proxy

def default_command(listen_port, host_url):
    proxy = comsoljupyter.proxy.ComsolProxy(listen_port, host_url)
    proxy.listen()
    reactor.run()

default_command(8080, 'https://comsol.radiasoft.org')
