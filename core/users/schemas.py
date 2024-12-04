from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from core.users import serializers

user_send_code_schema = extend_schema(
    summary="User send code",
    request=serializers.SendCodeSerializer,
    responses={
        200: '',
        400: {"example": {'error_code': 'error_code'}},
        429: {"example": {"detail": "Request was throttled. Expected available in (number) seconds."}},
    }
)

user_verify_code_schema = extend_schema(
    summary="User verify code",
    request=serializers.VerifyCodeSerializer,
    responses={
        200: '',
        400: {"example": {'error_code': 'error_code'}},
        429: {"example": {"detail": "Request was throttled. Expected available in (number) seconds."}},
    }
)

user_complete_registration_schema = extend_schema(
    summary="User complete registration",
    request=serializers.CompleteRegistrationSerializer,
    responses={
        200: serializers.VerificationResponseSerializer,
        400: {"example": {'error_code': 'error_code'}},
    }
)

user_reset_password_schema = extend_schema(
    summary="User reset password",
    request=serializers.ResetPasswordSerializer,
    responses={
        200: serializers.VerificationResponseSerializer,
        400: {"example": {'error_code': 'error_code'}},
    }
)

user_login_schema = extend_schema(
    summary="User login",
    request=serializers.LoginSerializer,
    responses={
        200: serializers.VerificationResponseSerializer,
        400: {"example": {'error_code': 'error_code'}},
        429: {"example": {"detail": "Request was throttled. Expected available in (number) seconds."}},
    }
)
