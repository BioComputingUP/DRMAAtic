.. include:: /path/to/project_logo.rst   # (optional project logo if available)

=============================
 DRMAAtic Documentation
=============================

**DRMAAtic** (Dramatically improve your cluster potential) is an open-source RESTful API service for job scheduling on HPC clusters. It provides a web interface to submit and control jobs on a cluster’s Distributed Resource Manager (e.g., SLURM). The core idea is that each computational **job** is defined as a pre-configured **task** with specific execution parameters. Users select a task, provide input parameters, and submit the job, which is then forwarded to the cluster’s scheduler via the DRMAA library. DRMAAtic assigns a unique UUID to each job so users can track status and retrieve results.

Key features of DRMAAtic include:

- **REST API for Job Control:** Submit jobs, monitor status, and download results via HTTP requests.
- **Cluster Integration:** Uses the **DRMAA** standard (with a SLURM implementation) for communicating with the cluster scheduler.
- **Built on Django REST Framework:** Leverages Django and DRF for robust API endpoints.
- **OAuth2 Authentication:** Integrates with external providers (e.g., ORCID) to issue JWT tokens for secure API access.
- **Docker Deployment:** Provided container images and compose files for easy setup on clusters.

.. note:: This documentation covers installation, usage and  development.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   developer_guide
