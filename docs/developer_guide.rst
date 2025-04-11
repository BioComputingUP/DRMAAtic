Developer Guide
===============

Architecture
------------

DRMAAtic is a Django-based web application structured as follows:

* **Django Project:** The ``server/`` directory contains the Django project configuration (settings, URLs, WSGI/ASGI entry points). It’s a standard Django project that configures the REST API endpoints and integrates with the DRMAA backend.

* **DRMAAtic App (``drmaatic/``):** This is the main Django app providing core functionality. Within this package:
* ``task/`` – a sub-app defining the **Task** model (the template for jobs), its serializer, and viewset. This app handles listing available tasks and (for admins) creating/editing tasks.
* ``job/`` – a sub-app (or module) for **Job** management. It includes the **JobViewSet** (registered at the ``/api/job/`` endpoint) which allows job submission and status retrieval. The Job model and logic interface with DRMAA to actually submit jobs to SLURM and fetch their status.
* Other modules in ``drmaatic/`` – e.g., ``authentication.py`` (custom OAuth2 logic for ORCID login), ``permissions.py`` (access control classes), ``utils.py`` (helper functions for job submission, file handling, etc.), and Django standard files like ``models.py``, ``views.py`` (for miscellaneous API views), ``urls.py`` (wiring the routers).
* **Dependencies:** Key dependencies include **Django REST Framework** (for building the API views/serializers) and **drmaa-python** (Python bindings for the DRMAA library, enabling DRMAAtic to communicate with SLURM’s job scheduler). Ensure the SLURM DRMAA library is installed on the system or container so that ``drmaa-python`` can connect to it.

DRMAAtic’s design follows a typical pattern: the Task and Job viewsets together provide a full cycle of job management. **TaskViewSet** (read-only to users) exposes what can be run, and **JobViewSet** handles creation of jobs and retrieval of their status/output. Under the hood, when a job is submitted, the system generates a shell script or command based on the Task, then uses `drmaa` to submit this to Slurm. The job’s unique ID (UUID) and possibly the cluster’s job ID are recorded. The DRMAA interface is then used to poll job status and fetch results, which are stored under a designated output directory on the server.

- Django project under `server/`
- Main app: `drmaatic/` with `task/` and `job/` modules
- Uses Django REST Framework and drmaa-python

Setting Up a Development Environment
------------------------------------
If you are planning to modify DRMAAtic or contribute, follow these steps:

1. **Fork and Clone** the repository to your GitHub account, then clone your fork locally.
2. **Install dependencies** in a virtual environment:

.. code-block:: bash
   
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt -r dev-requirements.txt
   
(Assume dev-requirements.txt might include additional tools like linters or test frameworks.) 

3. **Database and DRMAA setup:** For development, you can use the Docker-based SLURM cluster in ``docker/testing`` to have a local scheduler and database. Start that environment and configure your local Django to connect to the provided DB, or alternately install SLURM locally (which can be complex). Using the Docker test cluster is often easiest: after ``docker-compose`` up in ``docker/testing``, your local DRMAAtic code can connect to ``localhost:3306`` (MySQL) and ``localhost:6818`` (SLURM’s DRMAA) if properly configured. 

4. Apply migrations and create superuser (same as in Installation steps) to set up the database. 

5. Run the server in development mode and ensure you can hit the API and that jobs submitted go to the test SLURM.

Running Tests
-------------

The repository includes a ``tests/`` directory (Django tests) to verify functionality. To run the test suite:

.. code-block:: bash

   python manage.py test
   
Make sure the test environment can access a SLURM instance or consider using a simulated DRMAA environment. Some tests might be integration tests that expect the DRMAA backend to be available (perhaps the CI uses the Docker test cluster in headless mode). Continuous integration (GitHub Actions) is configured (see ``.github/workflows/``) to run tests and build Docker images on new commits. As a contributor, ensure that all tests pass before submitting a pull request.   

Advanced Configuration
----------------------

A few configuration points for advanced users or sysadmins:

* Settings and ``.env`` files: DRMAAtic’s Django settings are likely split for different environments. The server/settings/ may contain multiple settings files (production, development) and rely on .env files for secrets/keys (the deploy docs mention environment files. Check ``server/settings.py`` or ``server/utils.py`` for how environment variables are loaded. To customize, you can override these in your deployment (for example, set environment variables in your Docker compose or host).
* Authentication providers: By default, ORCID OAuth is enabled. You can add other OAuth2 providers by extending the SocialProviderAuthentication class or adding Django Allauth configurations. Ensure to update the front-end/client to support any new providers.
* Job execution environment: The DRMAAtic container or server must have access to the cluster’s scheduling commands (e.g., ``sbatch`` if not using DRMAA, or the DRMAA library configured properly). In Docker, this is handled via the custom entrypoint script that sets up the environment for DRMAA. If you need to integrate with a different scheduler or a different DRMAA implementation, you might use Breathe and Doxygen to document any C/C++ components or interfaces (for example, if part of the DRMAA integration was written in C, Breathe would allow incorporating its documentation into Sphinx – however, in DRMAAtic’s case, the DRMAA usage is through drmaa-python, so standard autodoc covers it).
