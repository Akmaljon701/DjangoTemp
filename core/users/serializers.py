from datetime import timedelta

from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from core.users import models
from core.users.exceptions import raise_user_error, UserErrorCodes
from core.utils.chack_auth import generate_sms_code
from core.utils.messages import get_send_code_message
from core.utils.redis import Redis


def get_active_user(phone):
    return models.User.objects.get(phone=phone, is_active=True, role=models.UserRoles.USER)

def generate_access_token(user):
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=timedelta(days=365))
    return str(token)


class GetCurrentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'id',
            'full_name',
            'phone',
            'email',
            'date_of_birth',
            'device_tokens',
            'created_at',
        )


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=9, validators=[MinLengthValidator(9), MaxLengthValidator(9)])
    for_reset = serializers.BooleanField(default=False)

    def send_sms_code(self):
        phone = self.validated_data['phone']
        for_reset = self.validated_data['for_reset']

        if for_reset:
            self._check_user_existence(phone)

        code = generate_sms_code()
        message = get_send_code_message(code)

        Redis.save(
            phone=phone,
            code=code,
            verified=False,
            expire_time=300
        )
        return message, int(phone)

    def _check_user_existence(self, phone):
        try:
            models.User.objects.get(phone=phone, is_active=True, role=models.UserRoles.USER)
        except models.User.DoesNotExist:
            raise_user_error(
                UserErrorCodes.USER_NOT_FOUND,
                "User not found."
            )


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=9, validators=[MinLengthValidator(9), MaxLengthValidator(9)])
    code = serializers.IntegerField()

    def validate_code(self, value):
        if len(str(value)) != 4:
            raise_user_error(
                UserErrorCodes.LESS_PASSWORD,
                "Password must be exactly 4 characters long."
            )
        return value

    def verify_code(self):
        phone = self.validated_data['phone']
        code = self.validated_data['code']

        key, value_dict = Redis.get(phone)

        if not value_dict:
            raise_user_error(
                UserErrorCodes.EXPIRED_SMS_CODE,
                "SMS code has expired."
            )

        verification_code = value_dict['code']

        if code != verification_code:
            raise_user_error(
                UserErrorCodes.INCORRECT_SMS_CODE,
                "Incorrect sms code."
            )

        Redis.save(
            phone=phone,
            code=verification_code,
            verified=True,
            expire_time=300
        )


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    device_token = serializers.CharField(max_length=300, required=False, default=None, allow_null=True)

    class Meta:
        model = models.User
        fields = [
            'phone',
            'password',
            'full_name',
            'email',
            'date_of_birth',
            'device_token',
        ]

    @transaction.atomic()
    def complete_registration(self):
        phone = self.validated_data['phone']
        password = self.validated_data.pop('password')
        device_token = self.validated_data.pop('device_token')

        key, value_dict = Redis.get(phone)

        if not value_dict:
            raise_user_error(
                UserErrorCodes.EXPIRED_TIME_REGISTRATION,
                "The registration time has expired."
            )

        verified = value_dict['verified']
        if not verified:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG,
            )

        user = self.save(
            role=models.UserRoles.USER,
            type_registration=models.RegistrationTypes.PHONE,
            is_active=True
        )
        user.set_password(password)
        if device_token and device_token not in user.device_tokens:
            user.device_tokens.append(device_token)
        user.save()

        access_token =  generate_access_token(user),

        return access_token, user


class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    device_token = serializers.CharField(max_length=300, required=False, allow_null=True)

    @transaction.atomic()
    def reset_password(self):
        phone = self.validated_data['phone']
        password = self.validated_data['password']
        device_token = self.validated_data['device_token']

        key, value_dict = Redis.get(phone)

        if not value_dict:
            raise_user_error(
                UserErrorCodes.EXPIRED_TIME_REGISTRATION,
            "The registration time has expired."
            )

        verified = value_dict['verified']
        if not verified:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG
            )

        user = get_active_user(phone)
        user.set_password(password)

        if device_token and device_token not in user.device_tokens:
            user.device_tokens.append(device_token)

        user.save()
        access_token =  generate_access_token(user),

        return access_token, user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    device_token = serializers.CharField(max_length=300, required=False, allow_null=True)

    def login(self):
        phone = self.validated_data['phone']
        password = self.validated_data['password']
        device_token = self.validated_data['device_token']

        try:
            user = models.User.objects.get(phone=phone, is_active=True, role=models.UserRoles.USER)
        except models.User.DoesNotExist:
            raise_user_error(
                UserErrorCodes.USER_NOT_FOUND,
            "User not found."
            )

        if not user.check_password(password):
            raise_user_error(
                UserErrorCodes.INVALID_PASSWORD,
            "Invalid password."
            )

        if device_token and device_token not in user.device_tokens:
            user.device_tokens.append(device_token)
            user.save()

        access_token =  generate_access_token(user),

        return access_token, user


class VerificationResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=200)
    user = GetCurrentSerializer()


