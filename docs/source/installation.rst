Installation
============

This section describes how to get DRMAAtic up and running on your system.

**Prerequisites:**
- Linux environment
- SLURM with DRMAA library (or the provided Docker setup)
- Python 3.8+ or Docker Engine

Using Docker (Recommended)
--------------------------
1. Clone the repository and navigate to the docker directory:
   git clone https://github.com/BioComputingUP/DRMAAtic.git
   cd DRMAAtic/docker

2. Deploy a test cluster (including a SLURM simulator, database, and DRMAAtic) using the provided docker compose file:

.. code-block:: bash

   cd testing
   docker-compose up -d 
   
This will start a local SLURM controller, a compute node, a MySQL database, and the DRMAAtic REST API service in containers, creating a self-contained test cluster environment.

3. OR deploy with an existing cluster:

* Edit configuration files (like ``slurm.conf``, database settings, etc.) in ``/deploy/deploy-example/`` to match your cluster.
* Start the DRMAAtic container and connect it to your cluster’s SLURM and database:

.. code-block:: bash

   cd ../deploy-example
   docker-compose up -d

* After the container(s) are running, proceed to initial setup (database migrations and creating an admin user) as described below:

.. code-block:: bash
 
    docker exec -it drmaatic /opt/venv/bin/python3 manage.py migrate
    docker exec -it drmaatic /opt/venv/bin/python3 manage.py createsuperuser

Manual Installation
-------------------
1. Clone the repository and install Python dependencies:

.. code-block:: bash
   
   git clone https://github.com/BioComputingUP/DRMAAtic.git
   cd DRMAAtic
   pip install -r requirements.txt

Ensure you have SLURM installed on the host and its DRMAA library available (the drmaa Python package will interface with it).

2. Configure the database: By default DRMAAtic uses MySQL/MariaDB. Set up a database and update the Django settings (or ``.env`` files in ``server/settings/``) with the DB credentials. For example, create a MySQL database named drmaatic and update ``server/settings/.env`` accordingly.

3. Run database migrations to set up the schema:

.. code-block:: bash

   python manage.py makemigrations
   python manage.py migrate
   
This will create the necessary tables for tasks, users, etc. in the database.

4. Create a superuser account for the Django admin (to manage tasks, etc.):

.. code-block:: bash

  python manage.py createsuperuser
  
Follow the prompts to set up an admin username and password

5. Start the DRMAAtic server:

.. code-block:: bash

   python manage.py runserver
   
By default, this will run the development server at ``http://127.0.0.1:8000/``. You should now have the DRMAAtic API available (though without a running SLURM, job submission will not function).

.. NOTE:: Accessing the Web API: Once running, the API endpoints can be accessed via ``http://<server>/api/...`` (if using the development server or appropriate host/port for Docker). You can also log into the Django admin UI at ``http://<server>/admin/`` using the superuser credentials, to configure tasks and view job records.
