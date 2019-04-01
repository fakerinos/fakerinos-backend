from rest_framework import permissions


class StrictDjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = dict(permissions.DjangoObjectPermissions.perms_map)
    perms_map['GET'] = ['%(app_label)s.add_%(model_name)s']
