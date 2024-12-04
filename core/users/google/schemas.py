from drf_spectacular.utils import extend_schema, OpenApiParameter
from core.users.google import serializers

login_redirect_schema = extend_schema(
        summary="Login with google",
        request=None,
        responses={200: ''}
    )

callback_schema = extend_schema(
        summary="Callback from Google",
        request=None,
        parameters=[
            OpenApiParameter(
                name="code",
                type=str,
                description="Authorization code received from Google.",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="state",
                type=str,
                description="State parameter for CSRF protection.",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="error",
                type=str,
                description="Optional error message returned by Google.",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: serializers.GoogleCallBackResponseSerializer(),
            400: {"example": {"error_code": "error_code"}},
        },
    )