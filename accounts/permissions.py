from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to users with the Administrator role.
    """
    message = "Forbidden: Only Administrators have permission to perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role())

class IsEngineerUserRole(permissions.BasePermission):
    """
    Allows access to users with Engineer role.
    """
    message = "Forbidden: Only Engineers have permission to access this endpoint."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_engineer_role() or request.user.is_admin_role()))

class IsSupervisorUserRole(permissions.BasePermission):
    """
    Allows access to users with Supervisor or Administrator role.
    """
    message = "Forbidden: Only Supervisors have permission to view this resource."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_supervisor_role())

