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

JUPYTERHUB_BASE_URL = None
PREFIX = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')

PROXY = None

def cleanup():
    if PROXY is not None:
        PROXY.stop()

def init(state_path, jupyterhub_base_url):
    global PROXY, JUPYTERHUB_BASE_URL

    JUPYTERHUB_BASE_URL = jupyterhub_base_url
    PROXY = nginx_proxy.NginxProxy(state_path, jupyterhub_base_url)

def jupyterhub_auth(f):
    @functools.wraps(f)
    def wrapper(*a, **kw):
        cookie = flask.request.cookies.get(auth.cookie_name)
        if cookie:
            user = auth.user_for_cookie(cookie)
        else:
            user = None

        if user is not None:
            return f(user['name'], *a, **kw)

        return flask.redirect(
            auth.login_url+'?next={}'.format(urllib.parse.quote(flask.request.path)))

    return wrapper



@app.route(PREFIX + '/logout')
@jupyterhub_auth
def forget_comsol_session(username):
    user = orm.get_user_by_username(username)

    if user.session is not None:
        orm.delete(user.session)
        user.session = None

    return flask.redirect(JUPYTERHUB_BASE_URL)


@app.route(PREFIX)
@jupyterhub_auth
def get_comsol_session(username):
    user = orm.get_user_by_username(username)

    if user.session is not None and not twisted.is_comsol_session_active(user.session):
        app.logger.info('Found inactive session {rsessionid} on port {port} for {username}'.format(
            username=username, port=user.session.port, rsessionid=user.session.rsessionid))
        orm.delete(user.session)
        user.session = None

    if user.session is None:
        creds = orm.get_unused_credentials()
        if creds is not None:
            session = twisted.get_comsol_session(user, creds)
            if session is not None:
                orm.add(session)
            else:
                app.logger.error('Unable to initiate comsol session for {username}'.format(username=username))
        else:
            app.logger.error('Unable to find credentials for {username}'.format(username=username))

    if user.session is None:
        app.logger.error('Unable to start session for {username}'.format(username=username))
        flask.abort(HTTPStatus.CONFLICT.value)

    # Start Proxy Nginx and return redirect
    PROXY.add_session(user.session)

    r = flask.redirect('http://comsol.radiasoft.org:{}/app-lib'.format(user.session.listen_port))
    r.set_cookie(
        domain='.radiasoft.org',
        httponly=True,
        key=comsoljupyter.RSESSIONID,
        value=user.session.rsessionid,
    )

    time.sleep(0.5)

    app.logger.info('Session {rsessionid} on port {port} for {username}'.format(
        username=username, port=user.session.listen_port, rsessionid=user.session.rsessionid))

    return r
