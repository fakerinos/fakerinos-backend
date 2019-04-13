from rest_framework.exceptions import APIException
from rest_framework import status


class AlreadyInRoomException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot create room because you are already in one."
    default_code = 'bad_request'


class DeckNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Could not find the requested deck"
    default_code = 'not_found'


class NotInRoomException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "You are not in a room"
    default_code = 'bad_request'
