# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

from comsoljupyter.web import orm

orm.init()

def add_user(username, password):
    orm.add(orm.User(username, password))

def add_credentials(username, password):
    orm.add(orm.ComsolCredentials(username, password))
