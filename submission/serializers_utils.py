import os

from rest_framework import exceptions
from rest_framework.exceptions import ValidationError

from .models import Parameter, TaskParameter


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
    for param in parameters_of_task:
        param = Parameter.objects.get(script=task.task_name, name=param.name)
        # Param not private and user has set it
        if not param.private and param.name in user_param.keys():
            # If the validation on the creation fails then the task (and all related param) will be deleted
            try:
                if param.type == Parameter.Type.FILE.value:
                    ext = get_extension(param.name, user_param[param.name].name)
                    file_pth = "/home/alessio/projects/submission_ws/outputs/{}/{}.{}".format(task.pk, param.name, ext)
                    with open(file_pth, "wb+") as f:
                        for chunk in user_param[param.name].chunks():
                            f.write(chunk)
                    new_param = TaskParameter.objects.create(task=task, param=param, value=file_pth)
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
    return created_params


def create_task_folder(wd):
    # TODO : Change base path
    os.makedirs(os.path.join("/home/alessio/projects/submission_ws/outputs", str(wd)), exist_ok=True)
