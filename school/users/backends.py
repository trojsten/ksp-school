from django.utils.http import urlencode

from social_core.backends.oauth import BaseOAuth2


class TrojstenOAuth2(BaseOAuth2):
    name = "trojsten"
    AUTHORIZATION_URL = "https://login.trojsten.sk/oauth/authorize/"
    ACCESS_TOKEN_URL = "https://login.trojsten.sk/oauth/token/"
    ACCESS_TOKEN_METHOD = "POST"

    def get_user_details(self, response):
        return {
            "username": response.get("username"),
            "email": response.get("email"),
            "first_name": response.get("first_name"),
            "last_name": response.get("last_name"),
        }

    def user_data(self, access_token, *args, **kwargs):
        url = "https://login.trojsten.sk/api/me?" + urlencode(
            {"access_token": access_token}
        )
        return self.get_json(url)
