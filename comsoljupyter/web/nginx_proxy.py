# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from comsoljupyter import CSSESSIONID, JSESSIONID
import collections
import pkg_resources
import pykern.pkjinja
import signal
import subprocess


ProxiedSession = collections.namedtuple(
    'ProxiedSession',
    'port cssessionid jsessionid rsessionid'
)

class NginxProxy(object):
    _nginx_conf_template = pkg_resources.resource_filename(
        'comsoljupyter',
        'package_data/nginx_conf.jinja',
    )

    def __init__(self, state_path, jupyterhub_base_url):
        self._nginx_proc = None
        self._session_cookies = {}
        self._state_path = state_path
        self._jupyterhub_base_url = jupyterhub_base_url

    @property
    def _nginx_conf_file(self):
        return '{}/comsol_nginx.conf'.format(self._state_path)

    def _update_config(self):
        pykern.pkjinja.render_resource(
            'nginx_conf',
            {
                'jupyterhub_base_url': self._jupyterhub_base_url,
                'sessions': self._session_cookies.values(),
                'state_path': self._state_path,
            },
            self._nginx_conf_file,
        )

        if len(self._session_cookies) > 0:
            if self._nginx_proc is None:
                self._nginx_proc = subprocess.Popen(
                    [
                        'nginx', '-c', self._nginx_conf_file,
                        '-g', 'error_log stderr;',
                        '-p', self._state_path
                        ]
                )
            else:
                self._nginx_proc.send_signal(signal.SIGHUP)
        else:
            if self._nginx_proc is not None:
                n = self._nginx_proc
                self._nginx_proc = None
                n.kill()

    def add_session(self, session):
        p = ProxiedSession(
            cssessionid=session.cssessionid,
            jsessionid=session.jsessionid,
            port=session.listen_port,
            rsessionid=session.rsessionid,
        )

        if p.rsessionid in self._session_cookies:
            assert p == self._session_cookies[p.rsessionid]
        else:
            self._session_cookies[session.rsessionid] = p
            self._update_config()

    def delete_session(self, session):
        if session.rsessionid in self._session_cookies:
            del self._session_cookies[session.rsessionid]
            self._update_config()

    def stop(self):
        if self._nginx_proc is not None:
            self._nginx_proc.terminate()
            self._nginx_proc = None
