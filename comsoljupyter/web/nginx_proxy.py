# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from comsoljupyter.web import app, orm
import collections
import copy
import datetime
import glob
import iso8601
import os
import pkg_resources
import pykern.pkjinja
import shutil
import signal
import subprocess
import tempfile
import threading
import time

ACTIVITY_LINE_LEN = 60

class NginxProcessStoppedError(Exception): pass


class ActivityMonitor(threading.Thread):
    def __init__(self, state_path, nginx_process):
        super().__init__(daemon=True, name=self.__class__.__name__)

        assert nginx_process is not None

        self._activity_glob = os.path.join(state_path, 'nginx_activity.*.log')
        self._lock = threading.Lock()
        self._nginx_process = nginx_process
        self._state_path = state_path
        self._stats = {}

        self._check_nginx_alive()

    def _check_nginx_alive(self):
        if self._nginx_process.poll() is not None:
            raise NginxProcessStoppedError

    @staticmethod
    def _read_logs(files):
        stats = {}
        for filename in files:
            with open(filename, 'r') as f:
                f.seek(-ACTIVITY_LINE_LEN*3, 2)
                last = f.readlines()[-1]
                rsessionid, timestr = last.split(' ', 1)
                stats[rsessionid] = iso8601.parse_date(timestr)
        return stats

    def _rotate_logs(self, dest):
        rotated_files = []
        for logfilename in glob.iglob(self._activity_glob):
            dest_filename = os.path.join(
                dest,
                os.path.basename(logfilename),
            )
            shutil.move(logfilename, dest_filename)
            rotated_files.append(dest_filename)

        self._check_nginx_alive()
        self._nginx_process.send_signal(signal.SIGUSR1)
        return rotated_files

    def _run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.logger.info('Log temp dir {}'.format(temp_dir))
            while True:
                time.sleep(30)
                app.logger.debug('Initiating monitoring')
                self._check_nginx_alive()
                to_process = self._rotate_logs(temp_dir)
                stats = self._read_logs(to_process)
                self._update_stats(stats)

    def _update_stats(self, new_stats):
        with self._lock:
            self._stats.update(new_stats)

    def get_and_clear_stats(self):
        with self._lock:
            s = self._stats
            self._stats = {}
            return s

    def run(self):
        app.logger.info('ActivityMonitor started')
        try:
            self._run()
        except NginxProcessStoppedError:
            return


ProxiedSession = collections.namedtuple(
    'ProxiedSession',
    'port cssessionid jsessionid rsessionid'
)


class NginxProxy(threading.Thread):
    _nginx_conf_template = pkg_resources.resource_filename(
        'comsoljupyter',
        'package_data/nginx_conf.jinja',
    )

    def __init__(self, state_path, jupyterhub_base_url):
        super().__init__(name=self.__class__.__name__, daemon=True)

        self._continue = True
        self._jupyterhub_base_url = jupyterhub_base_url
        self._lock = threading.Lock()
        self._nginx_proc = None
        self._pid = None
        self._session_cookies = {}
        self._state_path = state_path

        self._update_config()
        self._monitor = ActivityMonitor(state_path, self._nginx_proc)

    @property
    def _nginx_conf_file(self):
        return '{}/comsol_nginx.conf'.format(self._state_path)

    @property
    def _nginx_pid(self):
        # Nginx seems to do some process shenanigans at startup, even if it
        # is setup to not daemonize. The PID pointed by the Popen is incorrect
        # and in order to send signals to the right process we need to rely on the
        # text file with the PID.
        if self._pid is None:
            with open(os.path.join(self._state_path, 'nginx_comsol.pid'), 'r') as f:
                self._pid = int(f.read())
        return self._pid

    def _nginx_reload_conf(self):
        app.logger.debug('Sending SIGHUP to Nginx PID {}'.format(self._nginx_pid))
        os.kill(self._nginx_pid, signal.SIGHUP)

    def _start_nginx(self):
        if self._nginx_proc is None:
            self._nginx_proc = subprocess.Popen(
                [
                    'nginx', '-c', self._nginx_conf_file,
                    '-g', 'error_log stderr;',
                    '-p', self._state_path
                    ]
            )

            return True

        return False

    def _update_config(self):
        with self._lock:
            session_cookies = copy.copy(self._session_cookies)

        pykern.pkjinja.render_resource(
            'nginx_conf',
            {
                'jupyterhub_base_url': self._jupyterhub_base_url,
                'sessions': session_cookies.values(),
                'state_path': self._state_path,
            },
            self._nginx_conf_file,
        )

        if not self._start_nginx():
            self._nginx_reload_conf()

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
            with self._lock:
                self._session_cookies[session.rsessionid] = p
            self._update_config()

    def delete_sessions(self, *sessions):
        changed = False
        for session in sessions:
            if session.rsessionid in self._session_cookies:
                with self._lock:
                    del self._session_cookies[session.rsessionid]
                changed = True

        if changed:
            self._update_config()

    def run(self):
        app.logger.info('NginxProxy started')
        self._monitor.start()

        while self._continue and self._monitor.is_alive():
            time.sleep(60*5)

            expired_sessions = set()

            stats = self._monitor.get_and_clear_stats()

            for rsessionid, last_access in stats.items():
                if datetime.datetime.now() - last_access >= datetime.timedelta(minutes=5):
                    s = orm.get_session_by_rsessionid(rsessionid)
                    if s is not None:
                        expired_sessions.add(s)

            orm.delete(*expired_sessions)
            self.delete_sessions(*expired_sessions)

    def stop(self):
        if self._nginx_proc is not None:
            self._nginx_proc.terminate()
            self._nginx_proc = None
        self._continue = False
