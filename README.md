# ComsolJupyter

Provides a [JupyterHub](https://github.com/jupyterhub/jupyterhub) service to authenticate and proxy Comsol sessions.

## Running Test Instance

:warning: Do not run on the public cloud, since the test instance does not provide any security at all.

### Requirements 

* docker

### Setup

Add a file named `integration-test/credentials.txt` with all the Comsol credentials you want to see into the system. The format is a space separated usernames and passwords:

```
<username1> <password1>
<username2> <password2>
...
```

Also point `jupyter.radiasot.org` and `comsol.radiasoft.org` to `localhost` by editing `/etc/hosts`.

### Execution

Run the following script:

```sh
cd integration-test
./test.sh
```
### Usage

Visit [`http://jupyter.radiasoft.org:8000/services/comsol`](http://jupyter.radiasoft.org:8000/services/comsol).


# License

License: http://www.apache.org/licenses/LICENSE-2.0.html

Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
