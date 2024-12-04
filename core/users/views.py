from core.users import services as svc
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny

from core.users import schemas
from core.utils.chack_auth import IPThrottle


@schemas.user_send_code_schema
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([IPThrottle])
def user_send_code(request):
    return svc.UserService(request).send_code()


@schemas.user_verify_code_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def user_verify_code(request):
    return svc.UserService(request).verify_code()


@schemas.user_complete_registration_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def user_complete_registration(request):
    return svc.UserService(request).complete_registration()


@schemas.user_reset_password_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def user_reset_password(request):
    return svc.UserService(request).rest_password()


@schemas.user_login_schema
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([IPThrottle])
def user_login(request):
    return svc.UserService(request).login()


