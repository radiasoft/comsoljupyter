# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

from comsoljupyter.web import orm


def add_credentials(username, password, state_path='/tmp'):
    """Add Comsol credentials to the database

    Args:
        username (str): Comsol user
        password (str): Comsol password
        state_path (str): Optional. Where will the SqlLite database will be stored.

    """
    orm.init(state_path)
    orm.add(orm.ComsolCredentials(username, password))
