from random import SystemRandom
from urllib.parse import urlencode
from django.conf import settings
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
import requests
import jwt
from attrs import define
from .config import google_raw_login_get_credentials
from ..exceptions import raise_user_error, UserErrorCodes


CALLBACK_API_URL = 'google-login/callback/'


class GoogleRawLoginFlowService:
    API_URI = CALLBACK_API_URL
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self._credentials = google_raw_login_get_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        return f"{domain}{api_uri}"

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()
        state = self._generate_state_session_token()
        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }
        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"
        return authorization_url, state

    def get_tokens(self, code: str):
        redirect_uri = self._get_redirect_uri()
        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG,
                "Failed to obtain access token from Google."
            )

        tokens = response.json()
        return GoogleAccessTokens(
            id_token=tokens["id_token"],
            access_token=tokens["access_token"]
        )

    def get_user_info(self, google_tokens: 'GoogleAccessTokens'):
        access_token = google_tokens.access_token
        response = requests.get(self.GOOGLE_USER_INFO_URL, params={"access_token": access_token})

        if not response.ok:
            raise_user_error(
                UserErrorCodes.SOMETHING_WENT_WRONG,
                "Failed to obtain user info from Google."
            )

        return response.json()


@define
class GoogleAccessTokens:
    id_token: str
    access_token: str

    def decode_id_token(self):
        decoded_token = jwt.decode(self.id_token, options={"verify_signature": False})
        return decoded_token
