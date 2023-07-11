from django.db.models import Q
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from school.users.models import User


def logout_url(request):
    return "https://id.trojsten.sk/oauth/logout"


class TrojstenOIDCAB(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        email = claims.get("email")
        id = claims.get("sub")
        if not email and not id:
            return User.objects.none()
        return User.objects.filter(Q(email__iexact=email) | Q(trojsten_id=id))

    def create_user(self, claims):
        user = User()
        self._set_user(user, claims)
        user.save()

        return user

    def update_user(self, user, claims):
        self._set_user(user, claims)
        user.save()

        return user

    def _set_user(self, user, claims):
        user.trojsten_id = claims.get("sub")
        user.email = claims.get("email")
        user.username = claims.get("preferred_username")
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
