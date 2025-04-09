.. include:: /path/to/project_logo.rst   # (optional project logo if available)

=============================
 DRMAAtic Documentation
=============================

**DRMAAtic** (Dramatically improve your cluster potential) is an open-source RESTful API service for job scheduling on HPC clusters. It provides a web interface to submit and control jobs on a cluster’s Distributed Resource Manager (e.g., SLURM)&#8203;:contentReference[oaicite:0]{index=0}. The core idea is that each computational **job** is defined as a pre-configured **task** with specific execution parameters. Users select a task, provide input parameters, and submit the job, which is then forwarded to the cluster’s scheduler via the DRMAA library&#8203;:contentReference[oaicite:1]{index=1}. DRMAAtic assigns a unique UUID to each job so users can track status and retrieve results.

Key features of DRMAAtic include:

- **REST API for Job Control:** Submit jobs, monitor status, and download results via HTTP requests&#8203;:contentReference[oaicite:2]{index=2}.
- **Cluster Integration:** Uses the **DRMAA** standard (with a SLURM implementation) for communicating with the cluster scheduler&#8203;:contentReference[oaicite:3]{index=3}.
- **Built on Django REST Framework:** Leverages Django and DRF for robust API endpoints&#8203;:contentReference[oaicite:4]{index=4}.
- **OAuth2 Authentication:** Integrates with external providers (e.g., ORCID) to issue JWT tokens for secure API access&#8203;:contentReference[oaicite:5]{index=5}.
- **Docker Deployment:** Provided container images and compose files for easy setup on clusters&#8203;:contentReference[oaicite:6]{index=6}.

.. note:: This documentation covers installation, usage, development, and a detailed API reference for DRMAAtic.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   developer_guide
   api_reference
