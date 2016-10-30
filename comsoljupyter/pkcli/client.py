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
def _run(base_url, user, password, cookie_path):
    global RET

    try:
        client = comsoljupyter.client.ComsolClient(base_url, user, password)

        logged = yield client.login()
        assert logged, 'Not logged'

        active = yield client.session_active()
        assert active, 'Session not active'

        client.save_cookie_jar(cookie_path)
    except:
        pkdebug.pkdp(pkdebug.pkdexc())
        RET = 1
    reactor.stop()

def default_command(base_url, user, password, cookie_path):
    reactor.callWhenRunning(_run, base_url, user, password, cookie_path)
    reactor.run()
    sys.exit(RET)
