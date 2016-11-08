# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

import comsoljupyter.web

def default_command(port=5000, debug=False):
    comsoljupyter.web.run(port=port, debug=debug)
