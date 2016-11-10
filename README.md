# ComsolJupyter

Provides a web application to proxy user sessions from a demo web app to Comsol User sessions.

## Requirements 

* vagrant
* VirtualBox

## Setup

This demo application works as inside a VirtualBox VM that serves as a MITM between the real application and the user.

:warning: This demo application does not use encryption; it is intended to be a demo and used locally. Do not run across a public network.

Start Vagrant:

```sh
cd comsoljupyter/vagrant
vagrant up
```

Setup your MITM domain:

```sh
sudo echo '192.168.33.10 comsol.radiasoft.org' >> /etc/hosts 
```

## Usage

All the commands must be executed within the Vagrant vm:

```sh
cd comsoljupyter/vagrant
vagrant ssh
```

### Create DB Info

Add a user:

```sh
comsoljupyter db add-user <username> <password>
```

Add Comsol credentials:

```sh
comsoljupyter db add-credentials <username> <password>
```

Star the Web application:

```sh
comsoljupyter web
```

Visit the followign URL: [`http://www.comsol.radiasoft.org:5000`](http://www.comsol.radiasoft.org:5000).


# License

License: http://www.apache.org/licenses/LICENSE-2.0.html

Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
