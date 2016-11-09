# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter.web
import os
import signal
import traceback

os.setpgrp()

def default_command(port=5000, debug=False):
    try:
        comsoljupyter.web.run(port=port, debug=debug)
    except:
        traceback.print_exc()
    finally:
        os.killpg(0, signal.SIGKILL)
