from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.shortcuts import redirect
from rest_framework.views import APIView
from .services import GoogleRawLoginFlowService
from ..exceptions import raise_user_error, UserErrorCodes
from ..models import User, UserRoles, RegistrationTypes

from .. import serializers as user_serializers
from core.users.google import serializers
from core.users.google import schemas


def get_user_by_email(user_email):
    try:
        user = User.objects.get(email=user_email, is_active=True, role=UserRoles.USER)
        return user
    except User.DoesNotExist:
        return False


class GoogleLoginRedirectApi(APIView):
    authentication_classes = []
    permission_classes = []

    @schemas.login_redirect_schema
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()
        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    @schemas.callback_schema
    def get(self, request, *args, **kwargs):
        input_serializer = serializers.GoogleCallBackInputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        code = input_serializer.validated_data.get("code")
        error = input_serializer.validated_data.get("error")
        state = input_serializer.validated_data.get("state")

        if error:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG,
                error
            )

        if not code or not state:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG,
                "Code and state are required."
            )

        session_state = request.session.get("google_oauth2_state")
        if not session_state or session_state != state:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG,
                "CSRF check failed."
            )

        del request.session["google_oauth2_state"]

        google_login_flow = GoogleRawLoginFlowService()
        google_tokens = google_login_flow.get_tokens(code=code)
        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]

        is_new_user = False

        user = get_user_by_email(user_email)
        if user is None:
            full_name = user_info.get("name", "")
            phone = user_info.get("phone", user_email)
            date_of_birth = user_info.get("birthdate", None)

            user = User.objects.create(
                phone=phone,
                full_name=full_name,
                email=user_email,
                date_of_birth=date_of_birth,
                role=UserRoles.USER,
                type_registration=RegistrationTypes.GOOGLE,
                is_active=True,
            )
            is_new_user = True

        access_token = user_serializers.generate_access_token(user),

        return Response(
            {
                "id_token_decoded": id_token_decoded,
                'access_token': access_token,
                'user': user_serializers.GetCurrentSerializer(user).data,
                'is_new_user': is_new_user
            },
            200
        )
