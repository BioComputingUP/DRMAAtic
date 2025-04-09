Installation
============

This section describes how to get DRMAAtic up and running on your system.

**Prerequisites:**
- Linux environment
- SLURM with DRMAA library (or Docker)
- Python 3.8+ or Docker Engine

Using Docker (Recommended)
--------------------------
1. Clone the repository and navigate to the docker directory:
   git clone https://github.com/BioComputingUP/DRMAAtic.git
   cd DRMAAtic/docker

2. Launch the test environment:
   cd testing
   docker-compose up -d

3. OR deploy with an existing cluster using:
   cd ../deploy-example
   docker-compose up -d

Post-install, run migrations and create a superuser:
   docker exec -it drmaatic /opt/venv/bin/python3 manage.py migrate
   docker exec -it drmaatic /opt/venv/bin/python3 manage.py createsuperuser

Manual Installation
-------------------
1. Clone and install dependencies:
   git clone https://github.com/BioComputingUP/DRMAAtic.git
   cd DRMAAtic
   pip install -r requirements.txt

2. Configure the database and run:
   python manage.py migrate
   python manage.py createsuperuser

3. Run the server:
   python manage.py runserver
