from rest_framework.permissions import BasePermission
from rest_framework.exceptions import MethodNotAllowed
from .models import AccessRoleRule, BusinessElement

class HasAccessPermission(BasePermission):
    message = "Доступ запрещен"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False  # 401

        element_name = getattr(view, 'business_element', None)
        if not element_name or not user.role:
            return False

        try:
            element = BusinessElement.objects.get(name=element_name)
            rule = AccessRoleRule.objects.get(role=user.role, element=element)
        except (BusinessElement.DoesNotExist, AccessRoleRule.DoesNotExist):
            return False
        if request.method == "GET" and (rule.read_permission or rule.read_all_permission):
            return True
        if request.method == "POST" and rule.create_permission:
            return True
        if request.method in ["PUT", "PATCH"] and (rule.update_permission or rule.update_all_permission):
            return True
        if request.method == "DELETE" and (rule.delete_permission or rule.delete_all_permission):
            return True

        return False  # 403
