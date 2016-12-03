# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter.web
import traceback


def default_command(port, jupyterhub_base_url, state_path='/tmp', debug=False):
    try:
        comsoljupyter.web.run(
            debug=debug,
            jupyterhub_base_url=jupyterhub_base_url,
            port=int(port),
            state_path=state_path,
        )
    except:
        traceback.print_exc()
    finally:
        comsoljupyter.web.cleanup()
