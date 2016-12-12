# -*- coding: utf-8 -*-

"""
Helper code to use the ComsolClient that is implemented as non-blocking
in a blocking environment, namely Flask.

:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter
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
        base_url='https://comsol.radiasoft.org',
        password=credentials.password,
        user=credentials.username,
    )

    twisted.internet.threads.blockingCallFromThread(
        twisted.internet.reactor,
        client.login,
    )

    if client.has_session and twisted.internet.threads.blockingCallFromThread(
            twisted.internet.reactor, client.session_active):

        return comsoljupyter.web.orm.ComsolSession(
            cookie_jar=client.cookie_jar,
            credential=credentials,
            cssessionid=client.CSSESSIONID.value,
            jsessionid=client.JSESSIONID.value,
            user=user,
        )

def is_comsol_session_active(session):
    if session is not None:
        client = comsoljupyter.client.ComsolClient(
            base_url='https://comsol.radiasoft.org',
            cookie_jar=session.cookie_jar,
            password=session.credential.password,
            user=session.credential.username,
        )

        return twisted.internet.threads.blockingCallFromThread(
            twisted.internet.reactor,
            client.session_active,
        )

    return False
