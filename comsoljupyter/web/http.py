# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from comsoljupyter.web import app, orm, twisted, nginx_proxy
from http import HTTPStatus
import comsoljupyter
import datetime
import functools
import html
import jupyterhub.services.auth
import os
import time
import urllib.parse

app.secret_key = 'super secret string'  # Change this!

import flask

auth = jupyterhub.services.auth.HubAuth(
    api_token=os.environ['JUPYTERHUB_API_TOKEN'],
    cookie_cache_max_age=60,
)

prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')

proxy = None

def cleanup():
    if proxy is not None:
        proxy.stop()

def init(state_path):
    global proxy

    proxy = nginx_proxy.NginxProxy(state_path)

def jupyterhub_auth(f):
    @functools.wraps(f)
    def wrapper(*a, **kw):
        cookie = flask.request.cookies.get(auth.cookie_name)
        if cookie:
            user = auth.user_for_cookie(cookie)
        else:
            user = None

        if user is not None:
            return f(str(user), *a, **kw)

        return flask.redirect(
            auth.login_url+'?next={}'.format(urllib.parse.quote(flask.request.path)))

    return wrapper

@app.route(prefix)
@jupyterhub_auth
def get_comsol_session(user):
    u = orm.get_user_by_username('pepe')

    if u.session is None:
        creds = orm.get_unused_credentials()
        if creds is not None:
            session = twisted.get_comsol_session(u, creds)
            orm.add(session)
        else:
            flask.abort(HTTPStatus.CONFLICT.value)

    # Start Proxy Nginx and return redirect
    proxy.add_session(u.session)

    r = flask.redirect('http://comsol.radiasoft.org:{}/app-lib'.format(u.session.listen_port))
    r.set_cookie(
        key=comsoljupyter.RSESSIONID,
        value=u.session.rsessionid,
        httponly=True,
    )

    time.sleep(0.5)

    return r
