from rest_framework.exceptions import APIException


class Conflict(APIException):
    status_code = 409
    default_detail = 'Conflict'
    default_code = 'conflict'

    def __init__(self, detail=None, code=None):
        super(Conflict, self).__init__(detail=detail, code=code)
