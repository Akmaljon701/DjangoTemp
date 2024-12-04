from django.db.models import IntegerChoices
from rest_framework.exceptions import APIException
from rest_framework import exceptions


class UserErrorCodes(IntegerChoices):
    SOMETHING_WENT_WRONG = 400_001
    USER_NOT_FOUND = 400_002
    LESS_PASSWORD = 400_003
    EXPIRED_SMS_CODE = 400_004
    INCORRECT_SMS_CODE = 400_005
    EXPIRED_TIME_REGISTRATION = 400_006
    INVALID_PASSWORD = 400_007


def user_exception(ExceptionClass, error_code: UserErrorCodes, message) -> APIException:
    exception = ExceptionClass({
        'error_code': error_code,
        'message': message,
    })
    return exception

def raise_user_error(error_code, message = "Something went wrong."):
    raise user_exception(
        exceptions.ValidationError,
        error_code,
        message,
    )

