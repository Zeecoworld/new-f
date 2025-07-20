# accounts/middleware.py
from datetime import timedelta
from django.conf import settings
from django.utils.timezone import now

class UpdateLastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user = request.user
            last_active = getattr(user, 'last_active', None)
            threshold = now() - timedelta(minutes=settings.LAST_ACTIVE_THRESHOLD)

            if last_active is None or last_active < threshold:
                user.last_active = now()
                user.save(update_fields=['last_active'])

        return response
