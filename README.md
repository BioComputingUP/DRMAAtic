# DRMAAtic: dramatically improve your cluster potential



At the core of the DRMAAtic architecture is the streamlined execution of jobs on a Distributed Resource Manager (DRM) such as SLURM. Each job is defined as an executable task with pre-configured parameters specifying how and where it will be run. These parameters include both system-level configurations and user-defined options provided at execution time. Users initiate a job by selecting a task, supplying the necessary inputs, and submitting it for execution. The job is then created and forwarded to the DRM, and a Universally Unique Identifier (UUID) is generated to allow users to track its progress and interact with it throughout its lifecycle.

DRMAAtic provides a RESTful API that allows users to submit, manage, and retrieve jobs and results. Communication with the DRM is handled via the [DRMAA APIs](https://en.wikipedia.org/wiki/DRMAA), specifically the SLURM implementation available here.

The DRMAAtic APIs are built using the Django REST Framework, and use [drmaa-python](https://github.com/pygridtools/drmaa-python?tab=readme-ov-file) as a bridge between Python and the SLURM-DRMAA implementation.

You can explore the full API documentation via the Swagger interface [here](https://drmaatic.biocomputingup.it/) and the full documentation [here](https://biocomputingup.github.io/DRMAAtic/).

