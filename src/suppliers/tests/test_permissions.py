import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.test import APIRequestFactory

from suppliers.permissions import IsAdminOrReadOnly
from users.models import User


@pytest.fixture
def api_request_factory() -> APIRequestFactory:
    return APIRequestFactory()


@pytest.fixture
def admin_user() -> User:
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        role="admin",
    )


@pytest.fixture
def regular_user() -> User:
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="regularpass123",
        role="buyer",
    )


@pytest.mark.django_db
class TestIsAdminOrReadOnly:
    def test_safe_methods_allowed_for_unauthenticated(
        self, api_request_factory: APIRequestFactory
    ) -> None:
        permission = IsAdminOrReadOnly()
        request = api_request_factory.get("/api/suppliers/")
        request.user = AnonymousUser()

        result = permission.has_permission(request, None)
        assert result is True

    def test_safe_methods_allowed_for_regular_user(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = IsAdminOrReadOnly()
        request = api_request_factory.get("/api/suppliers/")
        request.user = regular_user

        result = permission.has_permission(request, None)
        assert result is True

    def test_unsafe_methods_allowed_for_admin(
        self, api_request_factory: APIRequestFactory, admin_user: User
    ) -> None:
        permission = IsAdminOrReadOnly()
        request = api_request_factory.post("/api/suppliers/")
        request.user = admin_user

        result = permission.has_permission(request, None)
        assert result is True

    def test_unsafe_methods_denied_for_regular_user(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = IsAdminOrReadOnly()
        request = api_request_factory.post("/api/suppliers/")
        request.user = regular_user

        result = permission.has_permission(request, None)
        assert result is False

    def test_unsafe_methods_denied_for_unauthenticated(
        self, api_request_factory: APIRequestFactory
    ) -> None:
        permission = IsAdminOrReadOnly()
        request = api_request_factory.post("/api/suppliers/")
        request.user = AnonymousUser()

        result = permission.has_permission(request, None)
        assert result is False

    def test_all_safe_methods_work_for_all_endpoints(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = IsAdminOrReadOnly()
        endpoints = [
            "/api/suppliers/",
            "/api/supplier-offers/",
            "/api/supplier-promotions/",
            "/api/supplier-sales/",
        ]

        for endpoint in endpoints:
            for method in SAFE_METHODS:
                request = api_request_factory.generic(method, endpoint)
                request.user = regular_user

                result = permission.has_permission(request, None)
                assert result is True

    def test_all_unsafe_methods_require_admin_for_all_endpoints(
        self,
        api_request_factory: APIRequestFactory,
        regular_user: User,
        admin_user: User,
    ) -> None:
        permission = IsAdminOrReadOnly()
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        endpoints = [
            "/api/suppliers/",
            "/api/supplier-offers/",
            "/api/supplier-promotions/",
            "/api/supplier-sales/",
        ]

        for endpoint in endpoints:
            for method in unsafe_methods:
                request = api_request_factory.generic(method, endpoint)
                request.user = regular_user
                result = permission.has_permission(request, None)
                assert result is False

                request = api_request_factory.generic(method, endpoint)
                request.user = admin_user
                result = permission.has_permission(request, None)
                assert result is True
