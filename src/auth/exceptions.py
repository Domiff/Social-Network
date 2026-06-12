from src.core.exceptions import AppException


class AlreadyExists(AppException):
    DETAIL = "Already Exists"
    STATUS_CODE = 409


class DoesNotExists(AppException):
    DETAIL = "Does not Exists"
    STATUS_CODE = 404
