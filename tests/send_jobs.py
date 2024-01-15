import requests

FASTA_QUERY = ">DP0001\n" \
              "KADELERIRLRPGGKKKYRL"

base_endpoint = 'http://0.0.0.0:8301/'
# base_endpoint = 'https://dev.scheduler.biocomputingup.it/'

endpoint = {
    'job': base_endpoint + 'job/',
    'job_info': base_endpoint + 'job/{job_id}/',
    'job_files': base_endpoint + 'job/{job_id}/file/',
    'job_file': base_endpoint + 'job/{job_id}/file/{file_pth}',
}


def is_completed(status):
    return status in ['job finished normally', 'job finished, but failed']


if __name__ == '__main__':
    auth = False

    auth_header = {'Authorization': 'Bearer 714226e2-c151-4002-8845-caa41e754f5c'} if auth else None

    file = open('test.fasta', 'rb')

    # Send a new job to the scheduler
    job = requests.post(endpoint['job'], data=[('task', 'ring-v4')], headers=auth_header, files=[('input_file', file)])

    # Get the job id if the job was created
    if job.status_code == 201:
        job_id = job.json()['uuid']
        print(f'Job {job_id} created')

        # Send another job to the scheduler with the previous job as parent
        # job = requests.post(endpoint['job'], data={'task': 'test', 'parent_job': job_id, 'dependencies': job_id},
        #                     headers=auth_header)
        # if job.status_code == 201:
        #     job_id = job.json()['uuid']
        #     print(f'Job 2 {job_id} created')
        # else:
        #     print(f'Error creating job 2: {job.text}')
        #     exit(1)
    else:
        print(f'Error creating job: {job.text}')
        exit(1)
