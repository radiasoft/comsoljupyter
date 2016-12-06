c.Authenticator.admin_users = {'jupyterhub'}

c.JupyterHub.services = [
    {
        'command': [
            '/opt/conda/bin/comsoljupyter', 'web',
            '-s', '/srv/jupyterhub',
            '12345', 'http://jupyter.radiasoft.org:8000',
        ],
        'name': 'comsol',
        'url': 'http://127.0.0.1:12345',
    },
]
