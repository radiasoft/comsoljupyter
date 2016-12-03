# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter
import comsoljupyter.client
import comsoljupyter.web.orm
import http.cookiejar
import itertools
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
            user,
            client.CSSESSIONID.value,
            client.JSESSIONID.value,
            credentials,
        )

def is_comsol_session_active(session):
    if session is not None:
        kw = dict(itertools.zip_longest(
            '''version port port_specified domain_specified
            domain_initial_dot path path_specified secure expires
            discard comment comment_url rest'''.split(), [])
        )

        jar = http.cookiejar.CookieJar()
        for n, v in [
            (comsoljupyter.CSSESSIONID, session.cssessionid),
            (comsoljupyter.JSESSIONID, session.jsessionid),
        ]:
            # Cookie(
            #   version, name, value, port, port_specified, domain, domain_specified, domain_initial_dot,
            #   path, path_specified, secure, exres, discard, comment, comment_url, rest
            # )
            c = http.cookiejar.Cookie(
                name=n, value=v, domain='comsol.radiasoft.org',
                **kw,
            )

            jar.set_cookie(c)

        client = comsoljupyter.client.ComsolClient(
            base_url='https://comsol.radiasoft.org',
            cookie_jar=jar,
            password=session.credential.password,
            user=session.credential.username,
        )

        return twisted.internet.threads.blockingCallFromThread(
            twisted.internet.reactor,
            client.session_active,
        )

    return False
