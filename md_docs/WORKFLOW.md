# DRMAAtic — Project Workflow

> **DRMAAtic** (Dramatically improve your cluster potential) is a Django REST Framework service that exposes an HTTP API for submitting and managing HPC jobs on a SLURM cluster via the [DRMAA](https://en.wikipedia.org/wiki/DRMAA) standard.

---

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Component Overview](#2-component-overview)
3. [Authentication Workflow](#3-authentication-workflow)
4. [Task Management (Admin)](#4-task-management-admin)
5. [Job Submission Workflow](#5-job-submission-workflow)
6. [Job Lifecycle & Status States](#6-job-lifecycle--status-states)
7. [Job Monitoring Workflow](#7-job-monitoring-workflow)
8. [Output Retrieval Workflow](#8-output-retrieval-workflow)
9. [Job Deletion & Cleanup](#9-job-deletion--cleanup)
10. [Access Control & Throttling](#10-access-control--throttling)
11. [End-to-End Example (cURL)](#11-end-to-end-example-curl)
12. [Directory Structure Reference](#12-directory-structure-reference)

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client / User                        │
│              (curl, browser, external service)              │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DRMAAtic (Django)                         │
│                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │  Auth layer │   │  Task views  │   │   Job views     │  │
│  │  (ORCID /   │   │  /api/task/  │   │  /api/job/      │  │
│  │  Internal)  │   └──────────────┘   └────────┬────────┘  │
│  └──────┬──────┘                               │           │
│         │ JWT                         drmaa-python          │
│         ▼                                      │           │
│  ┌─────────────┐                               ▼           │
│  │  MySQL /    │                   ┌────────────────────┐  │
│  │  MariaDB    │◄──────────────────│  SLURM (via DRMAA) │  │
│  └─────────────┘                   └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- The **client** communicates exclusively through the REST API.
- **DRMAAtic** stores all metadata (users, tasks, jobs, parameters) in a relational database.
- Actual job execution is delegated to **SLURM** via the `drmaa-python` library.
- Output files are stored on the server filesystem under a per-job UUID directory.

---

## 2. Component Overview

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Django project config | `server/` | Settings, URL routing, WSGI/ASGI entry points |
| Core app | `drmaatic/` | Models (`User`, `Group`, `Token`), authentication, permissions, throttling, utilities |
| Task sub-app | `drmaatic/task/` | `Task` model & serializer; read-only for users, writable by admins |
| Job sub-app | `drmaatic/job/` | `Job` model & serializer; job submission, status updates, file access |
| Parameter sub-app | `drmaatic/parameter/` | `Parameter` & `JobParameter` models; defines and validates per-task inputs |
| Queue sub-app | `drmaatic/queue/` | `Queue` model; maps tasks to SLURM partitions with resource limits |
| Admin interface | Django admin | Full CRUD for tasks, queues, users, groups, and job management |
| DRMAA bridge | `drmaa-python` (external) | Submits jobs to SLURM, queries job status, terminates jobs |

---

## 3. Authentication Workflow

DRMAAtic supports two authentication methods:

### 3.1 External OAuth (ORCID)

```
Client                          DRMAAtic                        ORCID
  │                                │                               │
  │── GET /ORCID/token/ ──────────▶│                               │
  │                                │── OAuth2 authorization ──────▶│
  │                                │◀─ access token ───────────────│
  │                                │  (look up / create User)      │
  │◀── JWT (signed) ──────────────│                               │
  │                                │                               │
  │── API calls with               │                               │
  │   Authorization: Bearer <JWT>  │                               │
```

### 3.2 Internal Token

Administrators can create internal tokens directly via the Django admin. These are used for service-to-service or scripted access.

### 3.3 User Groups & Permissions

Every `User` belongs to a `Group` which controls:

- **Throttling rate** — maximum request burst per second.
- **JWT renewal time** — how long a token remains valid.
- **CPU credit** — a token-bucket that limits compute usage (max amount, regen rate).
- **Full access flag** — grants admin-level permissions when set to `True`.

Anonymous (unauthenticated) requests are served with the default `anonymous` group limits.

---

## 4. Task Management (Admin)

Tasks are the **templates** for jobs. They are configured once by an administrator and then available to all users.

### 4.1 Task Model Fields

| Field | Description |
|-------|-------------|
| `name` | Unique identifier for the task |
| `command` | Shell command / script to execute (e.g., `blast.sh`) |
| `_queues` | SLURM partitions/queues this task can run on |
| `cpus` | Number of CPUs per task |
| `memory` | RAM allocation |
| `_max_clock_time` | Wall-time limit (e.g., `"3 hours"`) |
| `is_array` | Whether the task is a SLURM job array |
| `begin/end/step_index` | Job array index range |
| `required_tokens` | CPU credits consumed per submission |
| `is_output_public` | Whether outputs are accessible without authentication |

### 4.2 Queue Model Fields

Each `Queue` attached to a `Task` defines:
- SLURM partition name
- Maximum CPU / memory caps

### 4.3 Parameter Model

Each `Task` can define one or more `Parameter` objects:
- **Type** (string, integer, file, flag, …)
- **Required / optional**
- **Default value**
- These are validated at submission time by `drmaatic/utils.py`.

---

## 5. Job Submission Workflow

```
Client                        DRMAAtic API                    SLURM
  │                               │                              │
  │─ POST /api/job/ ─────────────▶│                              │
  │  (task=<id>, params…, files…) │                              │
  │                               │ 1. Authenticate & throttle   │
  │                               │ 2. Validate parameters       │
  │                               │ 3. Save input files to disk  │
  │                               │ 4. Create Job record (DB)    │
  │                               │    status = RECEIVED         │
  │                               │ 5. Build DRMAA job template  │
  │                               │ 6. drmaa.runJob() ──────────▶│
  │                               │◀── SLURM job ID ─────────────│
  │                               │ 7. Store drm_job_id (DB)     │
  │                               │    status = CREATED          │
  │◀── 201 Created {uuid, …} ─────│                              │
```

**Key points:**
- Input files are uploaded as multipart form data and saved to `DRMAATIC_JOB_OUTPUT_DIR/<uuid>/`.
- The serializer (`drmaatic/job/serializers.py`) calls `process_parameters()` from `drmaatic/utils.py` to validate and format all parameters before submission.
- Child jobs (job arrays) are linked via the `parent_job` foreign key.
- Job **dependencies** (`afterany`, `afterok`, `afternotok`) can be declared at submission time; DRMAAtic passes these to SLURM's dependency mechanism.

---

## 6. Job Lifecycle & Status States

A job transitions through the following states:

```
                    ┌──────────┐
                    │ RECEIVED │  ← POST /api/job/ accepted
                    └────┬─────┘
                         │ DRMAA submission
                    ┌────▼─────┐
                    │ CREATED  │  ← drm_job_id assigned
                    └────┬─────┘
                         │ SLURM queues it
              ┌──────────▼──────────┐
              │    QUEUED_ACTIVE    │
              │   SYSTEM_ON_HOLD   │
              │    USER_ON_HOLD    │
              │ USER_SYSTEM_ON_HOLD│
              └──────────┬──────────┘
                         │ Scheduler runs it
                    ┌────▼─────┐
                    │ RUNNING  │
                    └────┬─────┘
              ┌──────────┴──────────┐
              │                     │
         ┌────▼────┐         ┌──────▼──────┐
         │  DONE   │         │   FAILED    │
         └─────────┘         └─────────────┘

  At any time:
  STOPPED        ← user calls PUT /api/job/<uuid>/stop/
  UNDETERMINED   ← DRMAA cannot determine status
  REJECTED       ← submission failed pre-checks
```

Status is stored in `Job._status` and is updated lazily whenever:
- The job is retrieved via the API (`GET /api/job/<uuid>/`).
- The status endpoint is polled (`GET /api/job/<uuid>/status/`).
- An admin triggers the "Update DRM status" action from the Django admin.

---

## 7. Job Monitoring Workflow

```
Client                         DRMAAtic API                   SLURM
  │                                │                              │
  │─ GET /api/job/<uuid>/ ────────▶│                              │
  │                                │── get_job_status(drm_id) ──▶│
  │                                │◀─ current SLURM state ───────│
  │                                │  (update DB if changed)      │
  │◀── 200 {uuid, status, …} ──────│                              │
```

Additional monitoring endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/job/` | `GET` | List all jobs belonging to the authenticated user |
| `/api/job/<uuid>/` | `GET` | Get full detail + current status for one job |
| `/api/job/<uuid>/status/` | `GET` | Lightweight status-only poll |
| `/api/job/?ids=uuid1,uuid2` | `GET` | Batch status check for multiple jobs |

---

## 8. Output Retrieval Workflow

Once a job reaches **DONE** status, output files are available under the job's UUID directory on the server.

```
Client                         DRMAAtic API
  │                                │
  │─ GET /api/job/<uuid>/file/ ───▶│  returns JSON list of files
  │                                │
  │─ GET /api/job/<uuid>/file/     │
  │       <filename> ─────────────▶│  streams the requested file
  │                                │
  │─ GET /api/job/<uuid>/download/ ▶│  streams a ZIP of all outputs
```

- The `file/` endpoint respects the `is_output_public` flag on the parent task — public outputs are accessible without authentication.
- Standard output (`<uuid[:8]>_out.txt`) and standard error (`<uuid[:8]>_err.txt`) files are **hidden from non-admin users** in the file listing.
- Admins can view stdout/stderr directly from the Django admin job list.

---

## 9. Job Deletion & Cleanup

| Action | Who | Effect |
|--------|-----|--------|
| `DELETE /api/job/<uuid>/` | Owner / admin | Sets `deleted = True`; removes files from filesystem |
| `PUT /api/job/<uuid>/stop/` | Owner / admin | Calls `drmaa.control(TERMINATE)` on the running job |
| Admin "Delete jobs in filesystem" | Admin only | Soft-deletes + filesystem removal in background thread |
| Admin "Delete and remove from database" | Admin only | Full hard delete from DB + filesystem |

Deleted jobs are **soft-deleted** by default (the `deleted` flag is set). They are excluded from user-facing list queries but remain in the database for audit purposes until a hard delete is performed.

---

## 10. Access Control & Throttling

### Permission Classes

| Class | Grants access to… |
|-------|-------------------|
| `IsOwner` | The user who submitted the job |
| `IsSuper` | Users whose group has `has_full_access = True` |
| `IsOutputAccessible` | Anyone, when the task's `is_output_public` is `True` |

### Throttling

Job **creation** uses a `TokenBucketThrottle` backed by the user's CPU credit pool:

```
cpu_credit_max_amount   — maximum credits (e.g., 100)
cpu_credit_regen_amount — credits added per regen cycle
cpu_credit_regen_time   — how often credits are added (e.g., "30 seconds")
required_tokens         — credits consumed per job submission
```

All other endpoints use burst-rate throttling (`IPRateThrottleBurst` / `UserBasedThrottleBurst`) defined per group.

---

## 11. End-to-End Example (cURL)

```bash
SERVER="https://drmaatic.example.org/api"

# 1. Obtain a JWT (via ORCID OAuth, or use an internal token)
TOKEN="<your_jwt_here>"

# 2. List available tasks
curl -H "Authorization: Bearer $TOKEN" "$SERVER/task/"

# 3. Submit a job (task ID = 5, with an input FASTA file)
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "task=5" \
  -F "input=@/path/to/sequence.fasta" \
  "$SERVER/job/")

UUID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['uuid'])")
echo "Job UUID: $UUID"

# 4. Poll status until DONE
while true; do
  STATUS=$(curl -s -H "Authorization: Bearer $TOKEN" "$SERVER/job/$UUID/status/")
  echo "Status: $STATUS"
  [[ "$STATUS" == *"DONE"* || "$STATUS" == *"FAILED"* ]] && break
  sleep 10
done

# 5. Download all results as a ZIP
curl -OJ -H "Authorization: Bearer $TOKEN" "$SERVER/job/$UUID/download/"

# 6. Or list individual output files
curl -H "Authorization: Bearer $TOKEN" "$SERVER/job/$UUID/file/"
```

---

## 12. Directory Structure Reference

```
DRMAAtic/
├── manage.py                   # Django management entry point
├── requirements.txt            # Python dependencies
│
├── server/                     # Django project configuration
│   ├── settings.py             # Main settings (reads from settings/)
│   ├── urls.py                 # Root URL dispatcher
│   └── utils.py                # Environment / settings helpers
│
├── drmaatic/                   # Main Django application
│   ├── models.py               # User, Group, Token models
│   ├── authentication.py       # ORCID / bearer token auth backends
│   ├── permissions.py          # IsOwner, IsSuper, IsOutputAccessible
│   ├── throttles.py            # CPU credit & burst throttle classes
│   ├── utils.py                # Parameter processing, file I/O helpers
│   ├── urls.py                 # API URL patterns
│   │
│   ├── task/                   # Task sub-app (job templates)
│   │   ├── models.py           # Task model
│   │   ├── serializers.py      # Task serializer
│   │   └── views.py            # TaskViewSet (read-only for users)
│   │
│   ├── job/                    # Job sub-app
│   │   ├── models.py           # Job model + status lifecycle
│   │   ├── serializers.py      # Job serializer (creates + submits)
│   │   └── views.py            # JobViewSet (submit, status, file, download)
│   │
│   ├── parameter/              # Parameter definitions per task
│   │   └── models.py           # Parameter, JobParameter models
│   │
│   ├── queue/                  # SLURM queue / partition mapping
│   │   └── models.py           # Queue model
│   │
│   └── migrations/             # Django database migrations
│
├── docker/
│   ├── testing/                # Self-contained SLURM test cluster
│   └── deploy-example/        # Production deployment with Apache
│
├── docs/                       # Sphinx documentation source
│   └── source/
│       ├── installation.rst
│       ├── user_guide.rst
│       └── developer_guide.rst
│
└── tests/                      # Integration test scripts
```

---

*For full API reference, visit the Swagger UI at the root of the running server, or the hosted version at [drmaatic.biocomputingup.it](https://drmaatic.biocomputingup.it/).*
