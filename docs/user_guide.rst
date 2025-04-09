User Guide
==========

This guide explains how to use DRMAAtic's API to submit and monitor cluster jobs.

Authentication
--------------
Authenticate via ORCID OAuth to receive a JWT token.
Use the token in Authorization headers for API requests:
   Authorization: Bearer <your_token>

Tasks
-----
- List available tasks:
   curl -H "Authorization: Bearer $TOKEN" https://<server>/api/task/

- View a task's detail:
   curl -H "Authorization: Bearer $TOKEN" https://<server>/api/task/<id>/

Submitting a Job
----------------
1. Upload input data (if needed)
2. Submit job:
   curl -X POST -H "Authorization: Bearer $TOKEN" -F "task=<TASK_ID>" -F "input=@input.dat" https://<server>/api/job/

3. Note the job UUID returned.

Monitoring Status
-----------------
Check job status:
   curl -H "Authorization: Bearer $TOKEN" https://<server>/api/job/<uuid>/

Retrieving Outputs
------------------
Download results:
   curl -OJ -H "Authorization: Bearer $TOKEN" https://<server>/api/job/<uuid>/download/

Example Workflow
----------------
Authenticate → List Tasks → Submit Job → Monitor → Download
