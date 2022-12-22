import json
import logging
import os
import zipfile
from pathlib import Path
from typing import List, Union

from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from server.settings import SUBMISSION_OUTPUT_DIR
from .parameter.models import Parameter, TaskParameter
from .task.models import Task

logger = logging.getLogger(__name__)


def format_value(value, param_type):
    if param_type == Parameter.Type.STRING.value:
        value = value.replace("'", "\''")
    value = value.strip()
    return value


def format_task_params(passed_params: List[TaskParameter]):
    formatted_params = []
    # Filter the parameters that are not supposed to go to the script, flag to_script = False
    passed_params = list(
            sorted(passed_params, key=lambda param: param.param.flag if param.param.flag else 0, reverse=False))
    for passed_param in passed_params:
        if passed_param.param.flag:
            # If the param is of type Bool and is positive, no value has to be passed, only the flag
            if passed_param.param.type == Parameter.Type.BOOL.value:
                formatted_params.append(passed_param.param.flag)
                continue

            value = format_value(passed_param.value, passed_param.param.type)
            if passed_param.param.flag[-1] == '=':
                formatted_params.append("{}{}".format(passed_param.param.flag, value))
            else:
                formatted_params.append(passed_param.param.flag)
                formatted_params.append(value)

        else:
            formatted_params.append(passed_param.value)

    return formatted_params


def get_extension(param_name, file_name):
    if '.' not in file_name:
        raise exceptions.NotAcceptable("The file parameter {} must have a file extension".format(param_name))

    # Extension is everything after the fist '.'
    extension = file_name.split('.')
    if len(extension) > 2:
        extension = extension[1:]
        return '.'.join(extension)
    else:
        return extension[-1]


def get_params(user_param, task: Task, parameters_of_task):
    created_params = set()
    renamed_files = dict()

    p_task = task.get_first_ancestor()
    for param in parameters_of_task:
        param = Parameter.objects.get(script=task.task_name, name=param.name)
        # Param not private and user has set it
        if not param.private and param.name in user_param.keys():
            # If the validation on the creation fails then the task (and all related param) will be deleted
            try:
                if param.type == Parameter.Type.FILE.value:
                    files = []
                    num_files = len(list(filter(None, user_param.getlist(param.name))))

                    if num_files == 0:
                        raise exceptions.NotAcceptable(
                                "The file for the parameter {} was not uploaded".format(param.name))

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
                        # Save the file to the output directory
                        with open(file_pth, "wb+") as f:
                            for chunk in file.chunks():
                                f.write(chunk)

                    files = ','.join(files)
                    new_param = TaskParameter.objects.create(task=task, param=param, value=files)
                else:
                    # Check that the length of the value is not greater than the max length of the field (5000)
                    if len(user_param[param.name]) > 5000:
                        raise exceptions.NotAcceptable(
                                "The value for the parameter {} is too long, the maximum permitted length is 5000"
                                .format(param.name)
                        )
                    user_param[param.name] = user_param[param.name].replace("\r\n", "\n")
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
        # Param is private and has to be set
        elif param.private:
            new_param = TaskParameter.objects.create(task=task, param=param, value=param.default)
            created_params.add(new_param)

    task.files_name = renamed_files

    # Write in a file all the association between new file name and original file name, if files are passed
    with open(os.path.join(SUBMISSION_OUTPUT_DIR, str(p_task.uuid), "files.json"), 'a') as f:
        json.dump(renamed_files, f)

    return created_params, renamed_files


def create_task_folder(wd):
    os.makedirs(os.path.join(SUBMISSION_OUTPUT_DIR, wd), exist_ok=True)


def zip_dir(dir_pth: Union[Path, str], filename: Union[Path, str]):
    # Convert to Path object
    dir_pth = Path(dir_pth)

    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in dir_pth.rglob("*"):
            zip_file.write(entry, entry.relative_to(dir_pth))


def get_ip(request):
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

    return ident


def request_by_admin(request):
    """
    Check if the request is made by an admin from the request
    """
    return request.user and request.user.is_admin()


def is_user_admin(context):
    """
    Check if the user is an admin from the context
    """
    user = getattr(context.get('request'), 'user', None)
    return user is not None and user.is_admin()
