import os
from django.core.exceptions import ImproperlyConfigured
from attrs import define

from dotenv import load_dotenv

load_dotenv()



@define
class GoogleRawLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    client_id = os.getenv("DJANGO_GOOGLE_OAUTH2_CLIENT_ID")
    client_secret = os.getenv("DJANGO_GOOGLE_OAUTH2_CLIENT_SECRET")
    project_id = os.getenv("GOOGLE_OAUTH2_PROJECT_ID")

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in settings.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in settings.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in settings.")

    return GoogleRawLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
        project_id=project_id
    )
