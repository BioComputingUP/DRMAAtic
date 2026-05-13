# DRMAAtic API Request Lifecycle (What Happens Exactly)

This document explains what happens internally when a user sends a request to DRMAAtic APIs, with special focus on POST /job.

## 1. Entry point in Django

Incoming HTTP requests first reach Django URL configuration in [server/urls.py](server/urls.py).

- The root path includes DRMAAtic routes from [drmaatic/urls.py](drmaatic/urls.py).
- Django admin is exposed separately at /admin/.

## 2. Route resolution in DRMAAtic

Inside [drmaatic/urls.py](drmaatic/urls.py):

- A DRF router registers job endpoints with JobViewSet.
- router.register(r'job', JobViewSet) maps:
  - GET /job/
  - POST /job/
  - GET /job/{uuid}/
  - DELETE /job/{uuid}/
- Additional explicit routes map custom actions like:
  - GET /job/{uuid}/status/
  - GET /job/{uuid}/download/
  - GET /job/{uuid}/file/{path}
  - PUT /job/{uuid}/stop/

## 3. View/controller that handles /job requests

Controller class: [drmaatic/job/views.py](drmaatic/job/views.py)

- Class name: JobViewSet
- Base class: ModelViewSet

For POST /job/, DRF uses the create action from ModelViewSet (inherited). Even though create is not explicitly overridden here, DRF still executes the standard create pipeline.

## 4. Request processing stages (generic for secured endpoints)

For a secured endpoint such as /job, DRF processes request in this order:

1. Authentication
2. Permission checks
3. Throttling checks
4. Request parsing (form/multipart/json)
5. Serializer validation
6. Business logic execution (create/list/retrieve/action)
7. Response serialization and HTTP response

In this project, the key implementations are in:

- Auth: [drmaatic/authentication.py](drmaatic/authentication.py)
- Permissions/throttles: [drmaatic/job/views.py](drmaatic/job/views.py)
- Creation logic: [drmaatic/job/serializers.py](drmaatic/job/serializers.py)

## 5. Authentication details for /job

Configured in JobViewSet:

- Session-style auth through the first DRF default auth class.
- Custom Bearer token auth through BearerAuthentication.

Bearer flow in [drmaatic/authentication.py](drmaatic/authentication.py):

1. Read Authorization header.
2. Match Bearer <token>.
3. Check token exists in Token table.
4. Decode/validate JWT signature, issuer, audience, expiry.
5. Resolve user and verify active status.
6. Attach user + token to request.

If any step fails, request is rejected before job creation starts.

## 6. What exactly happens for POST /job

Path: POST /job/

### 6.1 Controller phase

DRF routes request to JobViewSet create flow in [drmaatic/job/views.py](drmaatic/job/views.py).

Important hook inside view:

- perform_create calls serializer.save(user=request.user)

This is how ownership is attached to created jobs.

### 6.2 Serializer validation phase

Serializer class: JobSerializer in [drmaatic/job/serializers.py](drmaatic/job/serializers.py).

- The task field is required.
- First key custom validation for task is validate_task.
- validate_task does Task.objects.get(name=task).
- If not found, API returns NotFound.

This is the first important database lookup in the job creation path.

### 6.3 Serializer create phase

After validation, serializer.save calls JobSerializer.create(validated_data).

Inside create:

1. Read validated task from validated_data.
2. Enforce group-based task access.
   - If user is not allowed, returns Task not found.
3. Resolve optional parent_job.
4. Create Job model row in DB.
5. Set optional job_description and sender_ip.
6. Create output working folder for root jobs.
7. Load task parameters from Parameter table.
8. Process submitted parameters/files.
   - Validate required params.
   - Save uploaded files.
   - Build job parameter list.
9. Build DRMAA/SLURM submission parameters.
10. Process dependencies and dependency type.
11. Call start_job from drmaatic_lib.manage to submit to DRM.
12. If submission succeeds:
   - save drm_job_id
   - set status as created
13. If submission fails:
   - cleanup filesystem data when needed
   - set failed/rejected status and raise API error
14. Save final job state.
15. Optionally track analytics (Matomo).
16. Return created job instance.

Then DRF serializes the returned job and sends HTTP 201 Created.

## 7. What happens for GET /job and GET /job/{uuid}

Handled in [drmaatic/job/views.py](drmaatic/job/views.py):

- GET /job/ runs list.
  - Applies filters.
  - Restricts non-admin users to own non-deleted jobs.
  - Updates DRM status for returned jobs.
- GET /job/{uuid}/ runs retrieve.
  - Loads object via get_object.
  - Updates job DRM status.
  - Returns serialized data (or not found if deleted and non-admin).

## 8. Why users often see Task not found on POST /job

Common causes:

1. Wrong value in task field.
   - Must be task name, not script path.
2. User lacks group permission for that task.
   - Code intentionally returns not found for unauthorized task access.

This behavior is in JobSerializer validate/create logic in [drmaatic/job/serializers.py](drmaatic/job/serializers.py).

## 9. Minimal successful POST /job checklist

Before POST /job:

1. User authenticated (Bearer JWT or valid session).
2. task value equals an existing Task name.
3. User allowed to run that task by group rules.
4. Required task parameters provided with exact names.
5. File parameters sent as multipart upload.
6. Queue/resource limits valid for task.

## 10. Visual summary

Request -> Django URL resolver -> DRF router -> JobViewSet -> Auth -> Permissions -> Throttle -> Serializer validate -> JobSerializer.create -> DRMAA submit -> DB update -> Response

## 11. Main files to read for deep debugging

- [server/urls.py](server/urls.py)
- [drmaatic/urls.py](drmaatic/urls.py)
- [drmaatic/job/views.py](drmaatic/job/views.py)
- [drmaatic/job/serializers.py](drmaatic/job/serializers.py)
- [drmaatic/authentication.py](drmaatic/authentication.py)
