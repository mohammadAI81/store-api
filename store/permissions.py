from rest_framework import permissions
import copy


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Or User this (Delete request.method == 'GET')
        # if request.method in permissions.SAFE_METHODS:
        #    return True
        return bool((request.user and request.user.is_staff) or request.method == 'GET') 
    

class SendPrivateEmailToCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('store.send_private_email'))   
    
    
class CustomDjangoModelPermission(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']