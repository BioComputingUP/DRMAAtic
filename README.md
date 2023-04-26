# Submission scheduler WS Admin guide

This is a reference guide for the admin to configure and deploy the submission scheduler WS.

## Environments

There are three types of environments that defines the configuration and settings for the application. These 
settings comprehend the database connection, the logging level, the debug mode, the secret key, the allowed hosts,
and many others.
The environments are defined according to the setting file that is selected when the application is started.
Regarding the settings for now there are 4 different settings files:
 - `settings.py` - Base settings file. This file contains settings that are common to all environments.
 - `settings_dev.py` - Settings file for the development environment.
 - `settings_staging.py` - Settings file for the staging environment.
 - `settings_prod.py` - Settings file for the production environment.

### Dev

The dev environment is the environment that should be used in the developer machine. This can define a local database
like sqlite or mysql, it's running in debug mode, and it's logging level is set to DEBUG.

When developing the application, the developer should use the following commands to start the application with the 
correct settings (and environment):

        $ python manage.py makemigrations --settings=server.settings_dev
        $ python manage.py makemigrations submission --settings=server.settings_dev
        $ python manage.py migrate --settings=server.settings_dev
        $ python manage.py runserver 0.0.0.0:8300 --settings=server.settings_dev

Note the use of the `--settings` parameter to specify the settings file to use. Moreover, this triggers also the 
creation of the migrations (if needed) and the database migration. This is useful to keep the database schema in sync
with the models. This chain of commands can be set up in the PyCharm run configurations.

### Staging

The staging environment is the environment that should be used to create a development version of the application on 
the server. This is very useful to test the application on the same environment that will be used in production.
For example here there are all the queues and the connection to the Slurm cluster. 

For this environment the database is a mysql database, called `submission_ws_dev`, and it can replicate the production
database.

### Production

The production environment is the environment that is used in the production server (perse). This is the environment
that is used by all the applications in production (e.g. RING-3, CAID WS, PED, etc.). This env also uses a mysql database
called `submission_ws`.

## Databases

For the Staging and Production environments the database is a mysql database that is hosted on perse. The database
can be accessed using the credentials defined in the `/home/django/.my.env` file. It's already configured in order to
be also accessible with phpmyadmin as remote database from a machine inside the lab network.

Here is reported the database schema as of 2023-04-14:

<img width="650" src="/home/alessio/projects/submission_ws/figures/submission_scheme.png" alt="db scheme"/>

## Deploy

To deploy on Staging or Production, two bare repositories are being used. These are located in:
 - Staging: `/var/django/apps/scheduler_dev`
 - Production: `/var/django/submission` (for now, this will be changed in the future)

The deployment from the dev machine needs to be configured adding these two git remotes:

        $ git remote add staging django@perse:/var/django/apps/scheduler_dev.git
        $ git remote add production django@perse:/var/django/submission.git

When you have something new to deploy, you can do it so with (on e.g. staging):

        $ git push staging main

This will trigger a post-receive hook that will pull the changes from the bare repository, save the database on a temporary
directory and then restart the WSGI application.

**Note**: The post-receive hook do not perform any makemigrations or migrate commands. This is because the migrations
can require user interaction (e.g. when a new field is added to a model). This is why the migrations should be done
manually on the server.

### Apache WSGI

On our configuration, we use Apache as web server and mod_wsgi as WSGI module. The configuration for the WSGI application
is located in `/etc/apache2/sites-available/scheduler-dev.conf` (for the dev version).
This file contains the configuration for the WSGI application, the virtual host, and the SSL configuration.
Here is reported the configuration for the WSGI application for the staging environment:

    SetEnv DJANGO_ENV staging
    # wsgi app
    WSGIPassAuthorization On
    WSGIScriptAlias / /var/django/apps/${server_name}/server/wsgi.py
    WSGIDaemonProcess ${server_name} python-home=/home/django/miniconda3/envs/submission python-path=/var/django/apps/${server_name} user=django group=users
    WSGIProcessGroup ${server_name}

    # Set the environment to be staging (dev on perse)
    <Directory /var/django/apps/${server_name}/server>
            <Files wsgi.py>
                    Require all granted
            </Files>
    </Directory>

Note as the SetEnv directive is used to set the environment to staging. This is used by the wsgi.py file to load the
correct settings file and then start the application. For the production environment, the directive should be:

    SetEnv DJANGO_ENV production

## Manage.py

The migrations are handled by the `manage.py` script. This script is located in the main directory of the application
and it's used to perform all the database operations for the application.
The migrations are python files that are located in the `submission/migrations` directory. These files are created
automatically by the `manage.py` script when some changes in the models are detected. In some cases the user is asked
to create a migration file manually (for complex migrations). The migrations are used to keep the database schema in
sync with the models.

Some useful commands for the `manage.py` script are:
        
        # Creates a new superuser (admin) in interactive mode
        $ python manage.py createsuperuser --settings=server.settings_dev

        # Migrate the database to the migration 0023 (to go back to previous migrations)
        $ python manage.py migrate 0023 --settings=server.settings_dev


## Changelog Version 2.0.1

 1. The **Task** model has now been renamed **Job**, along with its related fields (e.g. parent_task is now parent_job and task_description to job_description. These changes also include the change in the endpoint, so /task/XYZ is now /job/XYZ. In the task you can also now configure the queue to use, how many processors and the amount of memory required for that task.
 2. The **Script** model has now been renamed **Task**. These changes also include the change in the endpoint, so /script/XYZ is now /task/XYZ.
 3. The **DRMJobTemplate** model no longer exists, and it has been divided into the new **Queue** model and the Task.
 4. The **Queue** model now hosts all the active queue (or partitions) reflecting the configuration of the cluster (Slurm in our case), and here the max amout of memory and the number of cpus available are configured. These confs will be used as validation when creating a new Task.
 5. We have a DEV scheduler WS! You can reach it at [dev.scheduler.biocomputingup.it](), and from now on it should be the endpoint that you will use while developing your application that needs a connection to the scheduler from your machine or from dev environment hosted in our server. **Only for in-production application the application can use the non-dev version of the scheduler.**
