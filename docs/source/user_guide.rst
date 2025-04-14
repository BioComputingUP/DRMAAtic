User Guide
==========

This guide explains how to use DRMAAtic to run jobs on the cluster through its REST API. We assume DRMAAtic is installed and running (see Installation), and you have access to an account.

Authenticating and Obtaining an API Token
-----------------------------------------

DRMAAtic uses OAuth for user authentication. In a typical setup, you will log in via an external provider (such as **ORCID**) to obtain a JWT access token. If using the provided front-end or Swagger UI, follow the login link to authenticate; otherwise, you can obtain a token by making a request to the authentication endpoint (as configured by the DRMAAtic server).

Use the token in Authorization headers for API requests:

.. code-block::

   Authorization: Bearer <your_token>
   
Without a valid token, most API endpoints (besides any public ones) will be inaccessible.


Tasks
-----

A **Task** in DRMAAtic represents a predefined job template or script that can be executed on the cluster. Each task includes the command or script to run and defines what input parameters are required. Tasks are usually configured by an administrator via the Django admin interface (or via an API, if provided).

* List available tasks:

Send a GET request to ``/api/task/`` to retrieve the list of tasks you can execute.
 
.. code-block:: bash

   curl -H "Authorization: Bearer $TOKEN" https://<server>/api/task/
   
This returns a JSON array of tasks, each with an id, name, description, and information on required inputs (for instance, a task might indicate it needs a FASTA file input or certain parameters).

* View a task's detail:

You can GET ``/api/task/<id>/`` to see details of a specific task, including default parameters or documentation on what it does.

.. code-block:: bash
   
   curl -H "Authorization: Bearer $TOKEN" https://<server>/api/task/<id>/

Submitting a Job
----------------

1. Upload input data (if needed)

Ensure you have the required input files accessible (if needed). Depending on configuration, you may upload inputs via the API or ensure the files are accessible on a shared filesystem. In many cases, DRMAAtic provides an endpoint or method to upload input files as part of the job submission.

2. Submit job: Make a POST request to the job submission endpoint. DRMAAtic’s API supports job submissions via the ``/api/job/`` endpoint.

.. code-block:: bash
   
   curl -X POST -H "Authorization: Bearer $TOKEN" -F "task=<TASK_ID>" -F "input=@input.dat" https://<server>/api/job/
   
In this example, we use a multipart form (``-F``) to send both the chosen task ID and an input file. You might also include other form fields or JSON parameters depending on the task (e.g., parameters like number of threads, etc.). The exact API contract for job submission (field names, upload method) will be defined in the API reference.

3. Receive job UUID: If the submission is successful, the API will respond with a JSON containing the newly created job’s unique identifier (UUID) and initial status. For instance:

.. code-block:: json

   {
     "id": "123e4567-e89b-12d3-a456-426614174000",
     "task": 42,
     "status": "QUEUED",
     "submit_time": "2025-04-09T14:30:00Z",
    ...
   }

Note the ``id`` field, which is the job’s UUID. You will use this to query the job status or results.


Monitoring Status
-----------------

* Check job status: GET ``/api/job/<job_uuid>/`` to retrieve the current status and details of the job. The status may be QUEUED, RUNNING, COMPLETED, FAILED, etc., reflecting the scheduler’s state. For example:

.. code-block:: bash

   curl -H "Authorization: Bearer $TOKEN" https://<server>/api/job/<uuid>/
   
The response might include fields like status, ``exit_code``, ``start_time``, ``end_time``, and any output metadata.

* Auto-refresh: (If using a web front-end or the browsable API interface, you might see the status update periodically. Otherwise, you can poll the status with the above GET call.)

DRMAAtic uses the DRMAA library under the hood to query the cluster about the job’s state, rather than maintaining its own separate job tracking database. This means the status is always in sync with the cluster scheduler.

Retrieving Outputs
------------------
* List output files: Once status is COMPLETED, you can GET ``/api/job/<job_uuid>/output/`` (endpoint name may vary) to get a listing of output files produced by the job. DRMAAtic typically aggregates outputs under a directory named after the job’s UUID on the server. A JSON response may list file names, sizes, and possibly URLs.


* Download output: for convenience, an endpoint may provide a packaged download (e.g., a zip archive of the job’s output directory). For example:

.. code-block:: bash

   curl -OJ -H "Authorization: Bearer $TOKEN" https://<server>/api/job/<uuid>/download/
   
It would download a file (e.g., <uuid>.zip) containing all results. Alternatively, the API might give URLs per file which you can download individually.

Example Workflow
----------------

1. Authenticate via ORCID, obtain ``TOKEN``.

.. code-block:: bash

   curl -H "Authorization: Bearer $TOKEN" https://api.drmaatic.example.org/api/task/

2. List tasks to find your desired computation:

.. code-block:: bash

    curl -X POST -H "Authorization: Bearer $TOKEN" -F "task=5" -F "input=@seq.fasta" \ 
     https://api.drmaatic.example.org/api/job/
     
3. Submit job (e.g., task 5 with an input file):

.. code-block:: bash

    curl -X POST -H "Authorization: Bearer $TOKEN" -F "task=5" -F "input=@seq.fasta" \ 
     https://api.drmaatic.example.org/api/job/
     
-> returns ``{"id": "...UUID...", "status": "QUEUED", ...}``
     
4. Monitor status until completion:

.. code-block:: bash

   curl -H "Authorization: Bearer $TOKEN" https://api.drmaatic.example.org/api/job/<UUID>/
   
(repeat until ``"status": "COMPLETED"``)

5. Download results:

.. code-block:: bash

   curl -OJ -H "Authorization: Bearer $TOKEN" https://api.drmaatic.example.org/api/job/<UUID>/download/
   
(The ``-OJ`` flags instruct curl to save the file with the server-provided filename.)
