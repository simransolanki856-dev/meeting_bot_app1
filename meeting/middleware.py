import os
import base64
from django.conf import settings
from django.http import HttpResponse


class BasicAuthMiddleware:
    """Simple HTTP Basic Auth middleware controlled by env vars.

    Set the following environment variables to enable:
      PROTECT_WITH_BASIC_AUTH=True
      BASIC_AUTH_USERNAME=admin
      BASIC_AUTH_PASSWORD=changeme

    This is intended for staging/demo deployments where you want
    a quick password gate before adding full authentication.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.protect = getattr(settings, 'PROTECT_WITH_BASIC_AUTH', False)
        self.username = getattr(settings, 'BASIC_AUTH_USERNAME', '')
        self.password = getattr(settings, 'BASIC_AUTH_PASSWORD', '')

    def __call__(self, request):
        if not self.protect:
            return self.get_response(request)

        # Allow health checks and static/media
        path = request.path
        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return self._unauthorized()

        try:
            method, encoded = auth_header.split(' ', 1)
            if method.lower() != 'basic':
                return self._unauthorized()
            decoded = base64.b64decode(encoded).decode('utf-8')
            req_user, req_pass = decoded.split(':', 1)
        except Exception:
            return self._unauthorized()

        if req_user == self.username and req_pass == self.password:
            return self.get_response(request)

        return self._unauthorized()

    def _unauthorized(self):
        response = HttpResponse('Unauthorized', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Meeting Bot"'
        return response
