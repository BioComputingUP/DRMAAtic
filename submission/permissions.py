from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """ Grants access to owner
    
    This permission allows the owner to execute CRUD operations
    on a resource. If the resource is not owned by anyone, knowing
    the identifier of the resource will be sufficient. Instead, if
    the resource is owned by someone, accession token must be issued.
    """

    # Override `has_permission` method
    def has_permission(self, request, view):
        # Call parent method
        return super().has_permission(request, view)

    # Override `has_object_permission` method
    def has_object_permission(self, request, view, obj):
        # Retrieve user token from request
        user, token = request.user, request.auth
        # Check that object has user attribute
        if not hasattr(obj, 'user') or getattr(obj, 'user') is None:
            # Otherwise, just grant permission
            return True
        # Case given user matches expected one
        elif getattr(obj, 'user') == user:
            # Grant permission
            return True
        # Otherwise, do not grant permission
        else:
            return False


class IsSuper(BasePermission):
    """ Grants admin access to super users

    This permission allows the admin to execute CRUD operations
    on a resource.
    """

    # Override `has_object_permission` method
    def has_object_permission(self, request, view, obj):
        # Retrieve user token from request
        user, token = request.user, request.auth
        # Check that requesting user is an admin to give access to the obj
        if user is not None and user.is_admin():
            return True
        else:
            return False


class IsOutputAccessible(BasePermission):

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'task_name') and obj.task_name.is_output_visible:
            return True
        return False
