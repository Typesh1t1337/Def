from django.core.cache import cache
from django.utils.timezone import now

def set_user_online(user_id):
    cache.set(f'user_{user_id}', now(), timeout=100)

def is_user_online(user_id):
    return cache.get(f'user_{user_id}') is not None


class UpdateOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            set_user_online(request.user.id)
        return response

