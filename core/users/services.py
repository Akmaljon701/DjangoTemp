from rest_framework.response import Response
from core.users import serializers
from core.users.eskiz import sent_sms
from core.utils.pagination import BaseService, BaseServicePagination



class UserService(BaseService):
    def send_code(self):
        serializer = serializers.SendCodeSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        message, phone = serializer.send_sms_code()

        sent_sms(message, phone)

        return Response(status=200)

    def verify_code(self):
        serializer = serializers.VerifyCodeSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.verify_code()
        return Response(status=200)

    def complete_registration(self):
        serializer = serializers.CompleteRegistrationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        access_token, user = serializer.complete_registration()

        return Response(
            {
                'access_token': access_token,
                'user': serializers.GetCurrentSerializer(user).data
            },
            200
        )

    def rest_password(self):
        serializer = serializers.ResetPasswordSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        access_token, user = serializer.reset_password()

        return Response(
            {
                'access_token': access_token,
                'user': serializers.GetCurrentSerializer(user).data
            },
            200
        )

    def login(self):
        serializer = serializers.LoginSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        access_token, user = serializer.login()

        return Response(
            {
                'access_token': access_token,
                'user': serializers.GetCurrentSerializer(user).data
            },
            200
        )
