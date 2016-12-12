# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter.web
import traceback


def default_command(port, jupyterhub_base_url, state_path='/tmp', debug=False):
    """Start the comsoljupyter JupyterHub Service
    Args:
        port (str): TCP port where the service HTTP server will be listening to
        jupyterhub_base_url (str): JupyterHub base url
        state_path (str): path to directory where internal state information will be stored
    """
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
