# DRMAAtic: dramatically improve your cluster potential


The core of the DRMAAtic architecture is the execution of a job in a DRM (such as SLURM). Each job must be defined as an executable task with pre-configured parameters specifying how and where the task will be executed. These parameters also include a set of user-defined options provided at execution time. Users initiate job execution by selecting a task, providing necessary inputs, and submitting the job. The job is subsequently created and forwarded to the DRM for execution. A universally unique identifier (UUID) is generated for the job, allowing users to track its state and interact with it as needed.

DRMAAtic provides a REST API interface to submit and control jobs, as well as downloading its results. The connection of with the DRM is provided through the [DRMAA APIs](https://en.wikipedia.org/wiki/DRMAA), implemented for SLURM in this [repository](https://github.com/natefoo/slurm-drmaa).

DRMAAtic APIs where built using the Django REST Framework, and [drmaa-python](https://github.com/pygridtools/drmaa-python?tab=readme-ov-file) as interface between python and the implementation of the SLURM-DRMAA APIs.
Full references to the available APIs in DRMAAtic are available [here](https://drmaatic.biocomputingup.it/).

## Deployment

It is highly suggested to deploy DRMAAtic as Docker container, for full reference guide and examples on how to do that you can read the README in `docker/example` and `docker/deploy-example`. In the first case the enitre cluster structure is created with a `docker compose`, while in the latter only the DRMAAtic container is created.

## Manage.py

The migrations are handled by the `manage.py` script. This script is located in the main directory of the application
and it's used to perform all the database operations for the application.
The migrations are python files that are located in the `drmaatic/migrations` directory. These files are created
automatically by the `manage.py` script when some changes in the models are detected. In some cases the user is asked
to create a migration file manually (for complex migrations). The migrations are used to keep the database schema in
sync with the models.

Some useful commands for the `manage.py` script are:
        
        # Creates a new superuser (admin) in interactive mode
        $ python manage.py createsuperuser

        # Create the migrations
        $ python manage.py makemigrations

        # Migrate the database 
        $ python manage.py migrate
        
In the case of the container, after a change is made in the application, one can access the container shell and run the migrations.

## Authentication

The implemented authentication scheme is based on an OAuth authentication with a social provider (e.g. ORCID), then a JWT token is issued to the user and the user can use the token in order to perform authorized requests to DRMAAtic.
Additional social provider can be added by modifying the `SocialProviderAuthentication` class and adding a new social provider. The current Oauth authentication with ORCID was based on this [guide](https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/README.md).
The authentication process and an example is provided in the API reference describe above.

