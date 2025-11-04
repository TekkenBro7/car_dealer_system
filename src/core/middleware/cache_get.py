from typing import Optional

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

CACHE_TIMEOUT = 60 * 10

NO_CACHE_PATHS = [
    "/api/auth/verify/",
    "/api/auth/confirm-email/",
    "/api/auth/confirm-username/",
    "/admin/",
]


class CacheGETMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        if request.method != "GET":
            return None

        for p in NO_CACHE_PATHS:
            if request.path.startswith(p):
                return None

        key = "cache:" + request.get_full_path()
        cached = cache.get(key)
        if cached:
            return cached

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if request.method == "GET" and response.status_code == 200:
            for p in NO_CACHE_PATHS:
                if request.path.startswith(p):
                    return response
            key = "cache:" + request.get_full_path()
            cache.set(key, response, CACHE_TIMEOUT)
        return response
