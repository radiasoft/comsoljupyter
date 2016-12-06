# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from comsoljupyter.web import app, orm, twisted, nginx_proxy
from http import HTTPStatus
import comsoljupyter
import flask
import functools
import jupyterhub.services.auth
import os
import time
import urllib.parse

app.secret_key = 'super secret string'  # Change this!


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
    PROXY.start()

def jupyterhub_auth(f):
    @functools.wraps(f)
    def wrapper(*a, **kw):
        cookie = flask.request.cookies.get(auth.cookie_name)
        if cookie:
            user = auth.user_for_cookie(cookie)
        else:
            user = None

        if user is not None:
            return f(user, *a, **kw)

        return flask.redirect(
            auth.login_url+'?next={}'.format(urllib.parse.quote(flask.request.path)))

    return wrapper



@app.route(PREFIX + '/logout')
@jupyterhub_auth
def forget_comsol_session(jupyter_user):
    user = orm.get_user_by_username(jupyter_user['name'])

    if user.session is not None:
        PROXY.delete_sessions(user.session)
        orm.delete(user.session)
        user.session = None

    return flask.redirect(JUPYTERHUB_BASE_URL)


@app.route(PREFIX)
@jupyterhub_auth
def get_comsol_session(jupyter_user):
    username = jupyter_user['name']
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


@app.route(PREFIX + '/sessions')
@jupyterhub_auth
def list_sessions(jupyter_user):
    if not jupyter_user['admin']:
        flask.abort(HTTPStatus.UNAUTHORIZED.value)

    stats = PROXY.activity_monitor.get_stats()

    o = {}
    for session in orm.ComsolSession.query.all():
        if session.rsessionid in stats:
            last_access = stats[session.rsessionid]
        else:
            last_access = None

        o[session.rsessionid] = {
            'credential': session.credential.username,
            'last_access': last_access,
            'port': session.listen_port,
            'user': session.user.username,
        }

    return flask.jsonify(**o)
