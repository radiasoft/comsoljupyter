# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import tornado.platform.twisted
tornado.platform.twisted.install()
from twisted.internet import reactor

from jupyterhub.spawner import Spawner
from jupyterhub.utils import random_port

class ComsolSpawner(Spawner):
    def load_state(self, state):
        super().load_state(state)

    def get_state(self):
        state = super().get_state()
        return state

    def clear_state(self):
        super().clear_state()

    async def start(self):
        pass

    async def poll(self):
        pass

    async def stop(self, now=False):
        pass
