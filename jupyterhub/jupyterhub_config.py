import os

## Generic
c.JupyterHub.admin_access = True
c.Spawner.default_url = '/lab'

## Authenticator
from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.generic import GenericOAuthenticator
from tornado.auth import OAuth2Mixin

class CustomMixin(OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = os.environ['OAUTH_AUTHORIZE_URL']
    _OAUTH_ACCESS_TOKEN_URL = os.environ['OAUTH_ACCESS_TOKEN_URL']

class CustomLoginHandler(OAuthLoginHandler, CustomMixin):
    pass

class CustomAuthenticator(GenericOAuthenticator):
    login_service = 'Custom Login'
    login_handler = CustomLoginHandler
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    userdata_url = os.environ['USERDATA_URL']
    token_url = os.environ['TOKEN_URL']
    oauth_callback_url = os.environ['OAUTH_CALLBACK']
    userdata_method = 'GET'
    userdata_params = {"state": "state"}
    username_key = os.environ['USERNAME_KEY']

c.JupyterHub.authenticator_class = CustomAuthenticator

c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        #whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)

## Docker spawner

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_IMAGE']
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
# See https://github.com/jupyterhub/dockerspawner/blob/master/examples/oauth/jupyterhub_config.py
c.JupyterHub.hub_ip = os.environ['HUB_IP']

# user data persistence
# see https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }

# Other stuff
c.Spawner.cpu_limit = 1
c.Spawner.mem_limit = '10G'

## Services
c.JupyterHub.services = [
    {
        'name': 'cull_idle',
        'admin': True,
        'command': 'python /srv/jupyterhub/cull_idle_servers.py --timeout=3600'.split(),
    },
]
