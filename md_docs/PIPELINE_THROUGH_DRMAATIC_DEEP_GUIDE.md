# Running Any Pipeline Through DRMAAtic (Deep Detailed Guide)

This guide explains, step by step, how to execute a script or full pipeline from another project through DRMAAtic, from environment setup to result download.

It is written for your local Docker setup in this repository.

## 1. What DRMAAtic does in the execution path

DRMAAtic is an API layer in front of SLURM.

- You define a Task (command + resources + allowed queues + parameter schema).
- A user submits a Job for that task through the API.
- DRMAAtic validates inputs and permissions.
- DRMAAtic submits the job to SLURM through DRMAA.
- DRMAAtic stores metadata and lets you query status and outputs.

Relevant project files:

- URL routes: [drmaatic/urls.py](drmaatic/urls.py)
- Root URL mount: [server/urls.py](server/urls.py)
- Job submission logic: [drmaatic/job/serializers.py](drmaatic/job/serializers.py)
- Job result endpoints: [drmaatic/job/views.py](drmaatic/job/views.py)
- Docker topology: [docker/testing/docker-compose.yml](docker/testing/docker-compose.yml)
- Runtime env for testing: [docker/testing/.testing-docker.env](docker/testing/.testing-docker.env)

---

## 2. Local execution topology (important before configuring tasks)

In this Docker setup:

- Host folder tests is bind-mounted into container path /data.
- Scripts directory inside container is configured as /data/scripts.
- Outputs directory inside container is configured as /data/outputs.

So:

- Put executable scripts on host in tests/scripts/.
- Job outputs will appear on host in tests/outputs/.

This mapping comes from:

- [docker/testing/docker-compose.yml](docker/testing/docker-compose.yml)
- [docker/testing/.testing-docker.env](docker/testing/.testing-docker.env)

---

## 3. Prerequisites checklist

1. Docker and Docker Compose available.
2. DRMAAtic stack up and healthy.
3. Admin access to create queues/tasks/parameters.
4. A user token path ready (ORCID exchange flow in this project).
5. Pipeline script and all required runtime dependencies available in containers.

Start stack:

```bash
cd docker/testing
sudo docker compose up -d --build
sudo docker compose ps
```

UI endpoints:

- API/Swagger: http://localhost:8301/
- Admin: http://localhost:8301/admin/
- phpMyAdmin: http://localhost:8080/

---

## 4. Prepare your pipeline script (from another project)

### 4.1 Place it where DRMAAtic can execute it

Copy your script (or wrapper script) to:

- tests/scripts/<your_pipeline>/<run_script>.sh

Example:

- tests/scripts/rnaseq/run.sh

Make it executable:

```bash
chmod +x tests/scripts/rnaseq/run.sh
```

### 4.2 Script contract recommendations

Use a robust shell script style:

```bash
#!/usr/bin/env bash
set -euo pipefail

# parse args, run tools, write outputs
```

Recommended behavior:

- Validate input args early.
- Exit non-zero on failure.
- Write logs to stdout/stderr.
- Write result files in current working directory or under /data/outputs.
- Avoid writing outside mounted paths.

### 4.3 Dependencies

If your script needs tools (python, bwa, samtools, etc.), they must be installed in the runtime environment where SLURM executes jobs.

In this test stack, verify dependencies in relevant containers before production use.

---

## 5. Configure DRMAAtic entities in Admin

Open admin: http://localhost:8301/admin/

### 5.1 Create or verify Queue

A Queue controls resource ceilings (CPU/memory constraints).

### 5.2 Create Task

Create a Task representing your pipeline command.

Key fields:

- name: unique task id, for example rnaseq_pipeline
- command: pipeline command path
- queues: one or more allowed queues
- cpus: CPUs per task
- mem: memory per node (MB)
- max clock time
- required tokens
- group visibility rules

### 5.3 Command path rules (critical)

DRMAAtic applies this behavior:

- If command is relative, it prepends DRMAATIC_TASK_SCRIPT_DIR.
- If command is absolute, it executes it as-is.

So either use:

- Relative command: rnaseq/run.sh
  - Resolved under /data/scripts/ => /data/scripts/rnaseq/run.sh

or:

- Absolute command: /data/scripts/rnaseq/run.sh

### 5.4 Add Task Parameters

Define parameters your script expects.

Typical mapping:

- sample_id: string
- threads: int
- paired: bool
- reads_1: file
- reads_2: file
- reference: string or file

Parameter names must match form keys sent in POST /job/.

---

## 6. Authentication flow for user execution

This project uses provider token exchange:

- GET /orcid/token/
- Header Authorization: Bearer <ORCID_ACCESS_TOKEN>
- Response returns DRMAAtic jwt

Then use that JWT for all API requests:

- Authorization: Bearer <DRMAATIC_JWT>

Endpoints are exposed from [drmaatic/urls.py](drmaatic/urls.py).

---

## 7. Full end-to-end user flow (first step to final result)

## Step 1: Check task availability for your user

```bash
curl -sS \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8301/task/
```

Inspect specific task:

```bash
curl -sS \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8301/task/rnaseq_pipeline/
```

If task is not visible, check group/permission settings in admin.

## Step 2: Submit job

### Example with file inputs

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $JWT" \
  -F "task=rnaseq_pipeline" \
  -F "sample_id=S01" \
  -F "threads=8" \
  -F "paired=true" \
  -F "reads_1=@/absolute/path/S01_R1.fastq.gz" \
  -F "reads_2=@/absolute/path/S01_R2.fastq.gz" \
  http://localhost:8301/job/
```

Expected response includes:

- uuid
- status
- creation_date

Save uuid as JOB_ID.

## Step 3: Poll status

```bash
curl -sS \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8301/job/$JOB_ID/status/
```

or full details:

```bash
curl -sS \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8301/job/$JOB_ID/
```

Repeat until finished (done/failed/stopped states).

## Step 4: List output files

```bash
curl -sS \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8301/job/$JOB_ID/file/
```

## Step 5: Download output

Download single file:

```bash
curl -sS \
  -H "Authorization: Bearer $JWT" \
  -o result.txt \
  http://localhost:8301/job/$JOB_ID/file/path/from/list.txt
```

Download packaged ZIP:

```bash
curl -sS -OJ \
  -H "Authorization: Bearer $JWT" \
  http://localhost:8301/job/$JOB_ID/download/
```

---

## 8. Running a multi-step pipeline (job chaining)

When your pipeline has stages, you can chain jobs using dependencies.

Fields in POST /job/:

- parent_job: UUID of ancestor context
- dependencies: comma-separated UUIDs
- dependency_type: afterok, afterany, afternotok

Example stage 2 after stage 1 success:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $JWT" \
  -F "task=stage2_task" \
  -F "parent_job=$JOB1" \
  -F "dependencies=$JOB1" \
  -F "dependency_type=afterok" \
  http://localhost:8301/job/
```

Use this pattern for DAG-like orchestration.

---

## 9. Observability and debugging

### 9.1 DRMAAtic logs

```bash
cd docker/testing
sudo docker compose logs -f drmaatic
```

### 9.2 SLURM logs

```bash
sudo docker compose logs -f slurmctld slurmdbd c1 c2
```

### 9.3 DB/API sanity checks

```bash
curl -I http://localhost:8301/
curl -I http://localhost:8301/admin/
```

### 9.4 Inspect persisted outputs on host

- tests/outputs/

---

## 10. Common errors and fixes

1. Task not found during submit
- Cause: wrong task name or user cannot access that task/group.
- Fix: verify task name and group permission.

2. Parameter missing or invalid
- Cause: POST keys do not match task parameter names/types.
- Fix: inspect GET /task/{name}/ and align request fields.

3. Script not found
- Cause: command path does not resolve from /data/scripts.
- Fix: verify file path and command style (relative vs absolute).

4. Permission denied on script
- Cause: script not executable.
- Fix: chmod +x script.

5. Job failed immediately
- Cause: missing dependencies or bad script arguments.
- Fix: check drmaatic and slurm logs; run script manually in equivalent environment.

6. Download endpoint returns not found
- Cause: job not finished or no output zip generated yet.
- Fix: wait for completion and confirm files through /job/{uuid}/file/.

---

## 11. Best practices for production-style usage

- Keep each task deterministic and versioned.
- Use wrapper scripts to normalize paths and environment.
- Validate all required params in script and fail fast.
- Keep output structure predictable.
- Use dependency chaining for multi-step pipelines.
- Use group-based access to control who can run which tasks.

---

## 12. Quick command cheat sheet

```bash
# start
cd docker/testing && sudo docker compose up -d --build

# list tasks
curl -H "Authorization: Bearer $JWT" http://localhost:8301/task/

# submit
curl -X POST -H "Authorization: Bearer $JWT" -F "task=<task_name>" http://localhost:8301/job/

# status
curl -H "Authorization: Bearer $JWT" http://localhost:8301/job/<uuid>/status/

# files
curl -H "Authorization: Bearer $JWT" http://localhost:8301/job/<uuid>/file/

# download zip
curl -OJ -H "Authorization: Bearer $JWT" http://localhost:8301/job/<uuid>/download/
```

---

If you want, the next practical step is to pick one concrete external script and I can provide:

1. exact Task field values
2. exact parameter definitions
3. exact submit command with your real inputs
4. expected output file layout
