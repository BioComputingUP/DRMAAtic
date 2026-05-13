# DRMAAtic User Flow (First Step to Final Result)

This guide explains what DRMAAtic does and how a user goes from authentication to downloading job results.

## What DRMAAtic does

DRMAAtic is a Django REST API that submits and monitors compute jobs on SLURM through DRMAA.

- You choose a predefined **Task** (script + resources + input rules).
- You submit a **Job** for that task.
- DRMAAtic sends the job to SLURM.
- You track status and download outputs from API endpoints.

Core routes are defined in [drmaatic/urls.py](drmaatic/urls.py) and mounted by [server/urls.py](server/urls.py).

---

## 0) Start the stack

From [docker/testing](docker/testing), start services:

- `sudo docker compose up -d --build`

Main local URLs:

- API + Swagger UI: `http://localhost:8301/`
- Django admin: `http://localhost:8301/admin/`
- phpMyAdmin: `http://localhost:8080/`

---

## 1) (Admin) Prepare tasks and queues

An admin defines:

- queues (cluster partitions/resources)
- tasks (command, allowed queues, cpu/mem/time)
- task parameters (string/int/file/bool)
- user/group permissions

You can do this from Django admin: `http://localhost:8301/admin/`.

---

## 2) Authenticate as a user

DRMAAtic exchanges a social provider token (ORCID) for a DRMAAtic JWT.

Endpoint:

- `GET /orcid/token/`

Pass your ORCID access token in the header:

- `Authorization: Bearer <ORCID_ACCESS_TOKEN>`

Response returns:

- `{ "jwt": "<DRMAATIC_JWT>" }`

Then use this JWT for all API calls:

- `Authorization: Bearer <DRMAATIC_JWT>`

(See `retrieve_internal_token()` in [drmaatic/views.py](drmaatic/views.py).)

---

## 3) Discover available tasks

- `GET /task/` → list tasks available to you
- `GET /task/{name}/` → inspect one task and its parameters

Use this step to know exactly which parameter names you must submit.

---

## 4) Submit a job

Submit to:

- `POST /job/`

Required field:

- `task=<task_name>`

Optional fields:

- task parameters (field names must match parameter names)
- file parameters as multipart file upload
- `job_description`
- dependency fields (`dependencies`, `dependency_type`, `parent_job`)

Example (multipart):

- `task=wait_task`
- `input=@test.fasta` (only if the selected task requires a file parameter named `input`)

Successful response contains a job UUID:

- `uuid`

(Job creation behavior is in `JobSerializer.create()` in [drmaatic/job/serializers.py](drmaatic/job/serializers.py).)

---

## 5) Monitor the job

Use the UUID from submit response:

- `GET /job/{uuid}/` (full job data)
- `GET /job/{uuid}/status/` (status only)

Typical lifecycle:

- received/created → queued → running → done/failed

---

## 6) Retrieve outputs

After completion:

- `GET /job/{uuid}/file/` → list generated files
- `GET /job/{uuid}/file/{path}` → read/download a specific file
- `GET /job/{uuid}/download/` → download ZIP of job output directory

(Implemented in [drmaatic/job/views.py](drmaatic/job/views.py).)

---

## 7) Optional operations

- Stop a running job: `PUT /job/{uuid}/stop/`
- Delete (logical delete + cleanup): `DELETE /job/{uuid}/`
- CPU credit check: `GET /cpu-credit/` and `GET /cpu-credit/?required=<n>`

---

## End-to-end quick checklist

1. Stack up and reachable at `http://localhost:8301/`
2. Get DRMAAtic JWT from `/orcid/token/`
3. List tasks from `/task/`
4. Submit job to `/job/` with `task=<name>` and needed params/files
5. Poll `/job/{uuid}/status/`
6. Download results from `/job/{uuid}/download/` (or read files via `/job/{uuid}/file/...`)

If step 4 fails, re-check task parameter names/types from `/task/{name}/` and ensure your user has permission for that task.
