from rest_framework.exceptions import APIException
from rest_framework import status


class AlreadyInRoomException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '"Cannot create room because you are already in one.'
    default_code = 'bad_request'
