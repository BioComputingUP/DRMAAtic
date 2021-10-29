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
        # # Define user and token classes
        # User, Token = self.user, self.token
        # Retrieve user token from request
        user, token = request.user, request.auth
        # # Check that both user and token are instances of given classes
        # if (not (isinstance(user, User) and (isinstance(token, Token)))):
        #     # Otheriwse, do not grant permission
        # Check that object has user attribute
        if (not hasattr(obj, 'user')):
            # Otherwise, just grant permission
            return True
        # Case given user matches expected one
        elif (getattr(obj, 'user') == user):
            # Grant permission
            return True
        # Otherwise, do not grant permission
        else:
            return False

