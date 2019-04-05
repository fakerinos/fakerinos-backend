from rest_framework import permissions


class StrictDjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = dict(permissions.DjangoObjectPermissions.perms_map)
    perms_map['GET'] = ['%(app_label)s.add_%(model_name)s']


class ObjectOnlyPermissions(permissions.DjangoObjectPermissions):
    def has_permission(self, request, view):
        return True
