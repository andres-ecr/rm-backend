from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin

class IsClientUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'client')

class IsGuardUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'userprofile') and not request.user.userprofile.is_admin

