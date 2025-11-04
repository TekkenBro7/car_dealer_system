from typing import Optional

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from core.config.cache import CacheConfig
from core.enums import HttpMethod

CACHE_TIMEOUT = CacheConfig.CACHE_TIMEOUT
NO_CACHE_PATHS = CacheConfig.NO_CACHE_PATHS


class CacheGETMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        if request.method != HttpMethod.GET:
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
        if request.method == HttpMethod.GET and response.status_code == 200:
            for p in NO_CACHE_PATHS:
                if request.path.startswith(p):
                    return response
            key = "cache:" + request.get_full_path()
            cache.set(key, response, CACHE_TIMEOUT)
        return response
