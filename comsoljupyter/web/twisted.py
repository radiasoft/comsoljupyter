# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter.client
import comsoljupyter.web.orm
import threading
import twisted.internet
import twisted.internet.threads

class TwistedThread(threading.Thread):
    def run(self):
        twisted.internet.reactor.run()

t = TwistedThread()
t.start()

def get_comsol_session(credentials):
    client = comsoljupyter.client.ComsolClient(
        'https://comsol.radiasoft.org',
        credential.username,
        credential.password,
    )

    twisted.internet.threads.blockingCallFromThread(
        twisted.internet.reactor,
        client.login,
    )

    assert client.has_session and client.session_active()

    return comsoljupyter.web.orm.ComsolSession(
        client.CSSESSIONID.value,
        client.JSESSIONID.value,
        credentials,
    )

