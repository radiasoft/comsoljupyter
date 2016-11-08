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
        twisted.internet.reactor.run(installSignalHandlers=False)

t = TwistedThread(daemon=True)
t.start()

def get_comsol_session(user, credentials):
    client = comsoljupyter.client.ComsolClient(
        'https://comsol.radiasoft.org',
        credentials.username,
        credentials.password,
    )

    twisted.internet.threads.blockingCallFromThread(
        twisted.internet.reactor,
        client.login,
    )

    assert client.has_session and \
        twisted.internet.threads.blockingCallFromThread(
            twisted.internet.reactor,
            client.session_active,
        )

    return comsoljupyter.web.orm.ComsolSession(
        user,
        client.CSSESSIONID.value,
        client.JSESSIONID.value,
        credentials,
    )

