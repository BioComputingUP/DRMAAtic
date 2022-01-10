import json
import os
import zipfile
from pathlib import Path
from typing import Union

from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from server.settings import SUBMISSION_OUTPUT_DIR
from .models import Parameter, Task, TaskParameter


def format_task_params(passed_params):
    formatted_params = []
    for passed_param in passed_params:
        # If the param is of type Bool and is positive, no value has to be passed, only the flag
        if passed_param.param.type == Parameter.Type.BOOL.value and passed_param.value:
            formatted_params.append("{}".format(passed_param.param.flag))
        else:
            # If at the end of the flag there is a '=' then no space is required between flag and value
            format_string = "{} {}"
            if passed_param.param.flag[-1] == "=":
                format_string = "{}{}"
            formatted_params.append(format_string.format(passed_param.param.flag, passed_param.value).strip())

    return formatted_params


def get_extension(param_name, file_name):
    if '.' not in file_name:
        raise exceptions.NotAcceptable("The file parameter {} must have a file extension".format(param_name))
    return file_name.split('.')[-1]


def get_params(user_param, task, parameters_of_task):
    created_params = set()
    renamed_files = dict()

    p_task = get_ancestor(task)
    for param in parameters_of_task:
        param = Parameter.objects.get(script=task.task_name, name=param.name)
        # Param not private and user has set it
        if not param.private and param.name in user_param.keys():
            # If the validation on the creation fails then the task (and all related param) will be deleted
            try:
                if param.type == Parameter.Type.FILE.value:
                    files = []
                    num_files = len(user_param.getlist(param.name))
                    for file_idx, file in enumerate(user_param.getlist(param.name)):
                        ext = get_extension(param.name, file.name)
                        # If multiple files are passed on the same input name, then save them with different names
                        if num_files > 1:
                            file_name = "{}_{}.{}".format(param.name, file_idx, ext)
                        else:
                            file_name = "{}.{}".format(param.name, ext)

                        # Save original file name and new file name to a dict
                        renamed_files.setdefault(file_name, file.name)
                        # Manage multiple files for a single parameter
                        files.append(file_name)
                        file_pth = os.path.join(SUBMISSION_OUTPUT_DIR, str(p_task.uuid), file_name)
                        with open(file_pth, "wb+") as f:
                            for chunk in file.chunks():
                                f.write(chunk)

                    files = ','.join(files)
                    new_param = TaskParameter.objects.create(task=task, param=param, value=files)
                else:
                    new_param = TaskParameter.objects.create(task=task, param=param,
                                                             value=user_param[param.name])
                created_params.add(new_param)
            except ValidationError as e:
                task.delete()
                raise e
        # Param is required and user did not set it
        elif param.required and param.name not in user_param.keys():
            task.delete()  # The submitted task was not created with proper params, destroy it
            raise exceptions.NotAcceptable("The parameter {} must be specified for the {} task"
                                           .format(param.name, task.task_name))
        # Param is private and hase to be set
        elif param.private:
            new_param = TaskParameter.objects.create(task=task, param=param, value=param.default)
            created_params.add(new_param)

    # Write in a file all the association between new file name and original file name, if files are passed
    with open(os.path.join(SUBMISSION_OUTPUT_DIR, str(p_task.uuid), "files.json"), 'a') as f:
        json.dump(renamed_files, f)

    return created_params


def create_task_folder(wd):
    # TODO : Change base path
    os.makedirs(os.path.join(SUBMISSION_OUTPUT_DIR, wd), exist_ok=True)


def zip_dir(dir_pth: Union[Path, str], filename: Union[Path, str]):
    # Convert to Path object
    dir_pth = Path(dir_pth)

    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in dir_pth.rglob("*"):
            zip_file.write(entry, entry.relative_to(dir_pth))


def get_ancestor(task: Task):
    while task.parent_task is not None:
        task = task.parent_task

    return task


def log_ip(logger, request):
    def get_ident(req):
        """
        Identify the machine making the request by parsing HTTP_X_FORWARDED_FOR
        if present and number of proxies is > 0. If not use all of
        HTTP_X_FORWARDED_FOR if it is available, if not use REMOTE_ADDR.
        """
        xff = req.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = req.META.get('REMOTE_ADDR')
        num_proxies = api_settings.NUM_PROXIES

        if num_proxies is not None:
            if num_proxies == 0 or xff is None:
                return remote_addr
            addrs = xff.split(',')
            client_addr = addrs[-min(num_proxies, len(addrs))]
            return client_addr.strip()

        return ''.join(xff.split()) if xff else remote_addr

    ident = get_ident(request)

    logger.info("IP {} has sent a new task".format(ident if len(ident) > 0 else '?'))
