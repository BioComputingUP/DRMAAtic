# Docker Configuration for DRMAAtic

This directory contains a Docker configuration for DRMAAtic that also instantiates a Slurm cluster for testing purposes.

This configuration will set up a cluster with:

- A master node (named `slurmctld`)
- A database used for both Slurm and DRMAAtic (named `mariadb`)
- PhpMyAdmin (named `phpmyadmin`) to easily manage the databases
- The slurmdbd daemon (named `slurmdbd`)
- Two compute nodes (named `c1` and `c2`)
- The DRMAAtic django application (named `drmaatic`)

The compose can be created with the following command:

```bash
docker compose up -d
```

When executing this configuration, Slurm, the slurm-drmaa library and DRMAAtic will be executed in debug mode, and
the Django application will be served by the Django development server. The user will be able to see all the logs
from the slurm-drmaa library and DRMAAtic in the drmaatic container:

```bash
docker logs -f drmaatic
```

Also, all the other containers will have their logs available in the same way.

### First run

Upon the first run, the database for DRMAAtic needs to be created, and the migrations executed.
This can be done by accessing the [phpMyAdmin interface](http://localhost:8080) as root (password is `pwd`), and
creating a database named `drmaatic`.

Then, the migrations can be executed by running the following command on the drmaatic container:

```bash
docker exec -it drmaatic python manage.py makemigrations
docker exec -it drmaatic python manage.py migrate
```

You should also create a superuser for the Django admin interface:

```bash
docker exec -it drmaatic python manage.py createsuperuser
```

### Configurations
The configuration files for DRMAAtic are `.env` files located in the settings folder, and are loaded by
the `docker-compose.yml` file.

By default, the docker-compose file will mount the tests folder as a volume in the drmaatic container, where
the results of the tests will be stored (output files, logs, scripts, etc.).
