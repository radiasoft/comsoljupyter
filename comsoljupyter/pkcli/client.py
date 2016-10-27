# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

from pykern import pkdebug
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
import comsoljupyter.client
import sys
import tempfile

RET = 0

@inlineCallbacks
def _run(base_url, user, password):
    global RET

    try:
        client = comsoljupyter.client.ComsolClient(base_url, user, password)

        logged = yield client.login()
        assert logged

        active = yield client.session_active()
        assert active

        print(client.CSSESSIONID.name, client.CSSESSIONID.value)
        print(client.JSESSIONID.name, client.JSESSIONID.value)
    except:
        pkdebug.pkdp(pkdebug.pkdexc())
        RET = 1
    reactor.stop()

def default_command(base_url, user, password):
    reactor.callWhenRunning(_run, base_url, user, password)
    reactor.run()
    sys.exit(RET)
