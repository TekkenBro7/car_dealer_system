import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory

from core.enums import ViewAction
from offers.permissions import HasConfirmedEmail, IsAdminOrSelf
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
        email_confirmed=True,
    )


@pytest.fixture
def regular_user() -> User:
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="regularpass123",
        role="buyer",
        email_confirmed=True,
    )


@pytest.fixture
def unconfirmed_user() -> User:
    return User.objects.create_user(
        username="unconfirmed",
        email="unconfirmed@example.com",
        password="unconfirmed123",
        role="buyer",
        email_confirmed=False,
    )


@pytest.mark.django_db
class TestIsAdminOrSelf:
    def test_admin_has_permission_for_list(
        self, api_request_factory: APIRequestFactory, admin_user: User
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get("/api/offers/")
        request.user = admin_user

        class MockView:
            action = ViewAction.LIST

        view = MockView()

        result = permission.has_permission(request, view)
        assert result is True

    def test_regular_user_no_permission_for_list(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get("/api/offers/")
        request.user = regular_user

        class MockView:
            action = ViewAction.LIST

        view = MockView()

        result = permission.has_permission(request, view)
        assert result is False

    def test_authenticated_user_has_permission_for_non_list_actions(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get(f"/api/offers/{regular_user.id}/")
        request.user = regular_user

        class MockView:
            action = ViewAction.RETRIEVE

        view = MockView()

        result = permission.has_permission(request, view)
        assert result is True

    def test_unauthenticated_user_no_permission(
        self, api_request_factory: APIRequestFactory
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get("/api/offers/")

        request.user = AnonymousUser()

        class MockView:
            action = ViewAction.LIST

        view = MockView()

        result = permission.has_permission(request, view)
        assert result is False

    def test_admin_has_object_permission(
        self,
        api_request_factory: APIRequestFactory,
        admin_user: User,
        regular_user: User,
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get(f"/api/offers/{regular_user.id}/")
        request.user = admin_user

        obj = regular_user

        result = permission.has_object_permission(request, None, obj)
        assert result is True

    def test_user_has_object_permission_for_own_objects(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get(f"/api/offers/{regular_user.id}/")
        request.user = regular_user

        obj = regular_user

        result = permission.has_object_permission(request, None, obj)
        assert result is True

    def test_user_no_object_permission_for_other_objects(
        self,
        api_request_factory: APIRequestFactory,
        regular_user: User,
        admin_user: User,
    ) -> None:
        permission = IsAdminOrSelf()
        request = api_request_factory.get(f"/api/offers/{admin_user.id}/")
        request.user = regular_user

        obj = admin_user

        result = permission.has_object_permission(request, None, obj)
        assert result is False


@pytest.mark.django_db
class TestHasConfirmedEmail:
    def test_confirmed_buyer_can_create(
        self, api_request_factory: APIRequestFactory, regular_user: User
    ) -> None:
        permission = HasConfirmedEmail()
        request = api_request_factory.post("/api/offers/")
        request.user = regular_user

        class MockView:
            action = ViewAction.CREATE

        view = MockView()

        result = permission.has_permission(request, view)
        assert result is True

    def test_unconfirmed_buyer_cannot_create_raises_permission_denied(
        self, api_request_factory: APIRequestFactory, unconfirmed_user: User
    ) -> None:
        permission = HasConfirmedEmail()
        request = api_request_factory.post("/api/offers/")
        request.user = unconfirmed_user

        class MockView:
            action = ViewAction.CREATE

        view = MockView()

        with pytest.raises(PermissionDenied):
            permission.has_permission(request, view)
