# Docker deploy configuration for DRMAAtic

This directory contains a Docker deploy configuration for DRMAAtic. It is intended to be used for the 
automatic deployment of DRMAAtic in a cluster, using Github Actions.
The action will build the Docker images and then push them to the BioComputing Docker registry.

### Deployment

To deploy, you first need to commit and push your changes to the `main` (for prod) or `dev` (for staging) branch. 
This will build and push the image to the private registry.

Then, you need to run the `start-staging.sh` or `start-prod.sh` script. This will copy the files that are needed 
in the server, and then run the correct `docker-compose.yml` file.

### First run

Upon the first run, the database for DRMAAtic needs to be created, and the migrations executed.
This can be done by accessing the correct database (e.g. using phpMyAdmin) as root (or user with write privileges), and
creating a database named `drmaatic` (or `drmaatic_dev` for staging environment).

Then, the migrations can be executed by running the following command on the drmaatic container:

```bash
docker exec -it drmaatic /opt/venv/bin/python3.8 manage.py makemigrations
docker exec -it drmaatic /opt/venv/bin/python3.8 manage.py migrate
```

You should also create a superuser for the Django admin interface:

```bash
docker exec -it drmaatic /opt/venv/bin/python3.8 manage.py createsuperuser
```

### Configurations
The configuration files for DRMAAtic are `.env` files located in the settings folder, and are loaded by
the `docker-compose.yml` file.


## User permissions

This is a tough one. In the Dockerfile, a new user is created, called `myuser`. This user has the same UID as the 
myuser user from our LDAP server (1'000'042). Moreover, a new group is created, called `users` which has 
the GID of the `users` group from our LDAP server (1'000'001) **minus 3000**, so **997'001**.
Why this is needed?
* In the docker server, where the docker daemon is installed, the user remapping is enabled, shifting the UID and GID of
  the user and group by 3000 (for example).
* The `myuser` user is the one that is used to run the Django application via the `mod_wsgi` module of Apache. This user
  is also the one that connects to the `slurmctld` daemon to interact with the cluster, and also at the same time it will
  write in the filesystem the directory for the job execution and its input files. 
* When sending the job to the cluster, it is necessary that the controller recognize the uid of the user sending the job
  as a valid user. The uid when sending the job is not shifted by 3000, so the `myuser` user in the container has to have
  the same UID as the `myuser` user in the LDAP server.
* When writing in the filesystem, the `myuser` user in the container has to have the same GID as the `users` group in the
  LDAP server, so that the files written by the container are accessible by the `myuser` user in the cluster, even if
  virtually they have different UIDs. This is made possible by having the same GID, one shifted by 3000 and the other not.
* In order to make possible to the `myuser` LDAP user to write in the directory of the job execution, the directory has
  to have the correct permissions. This is done in two ways:
  * By setting the correct permissions on the root job directory with `chmod g+s`
  * By having an `umask 0002` in the `/etc/profile` file of all the worker nodes, and by setting it also on the apache 
    config file, under the `WSGIDaemonProcess` directive. This will make sure that all the files created by the `myuser`
    user inside the container, will have the correct permissions to be read by the `myuser` user in the LDAP, using the
    `users` group.
If this doesn't make sense, it is because it doesn't. It is a mess, but it works.
