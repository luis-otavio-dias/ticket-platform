import pytest

from user.models import User


@pytest.mark.django_db
class TestCreateUser:
    def test_create_user_with_valid_data(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        assert user.email == "testuser@example.com"
        assert user.check_password("testpassword")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_with_name(self):
        user = User.objects.create_user(
            email="named@example.com",
            password="testpassword",
            name="Luis Otávio",
        )

        assert user.name == "Luis Otávio"

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError, match="email"):
            User.objects.create_user(
                email="",
                password="testpassword",
            )


@pytest.mark.django_db
class TestCreateSuperuser:
    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
        )

        assert user.is_staff
        assert user.is_superuser

    def test_superuser_without_is_superuser_raises(self):
        with pytest.raises(ValueError, match="is_superuser"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpassword",
                is_superuser=False,
            )

    def test_superuser_without_is_staff_raises(self):
        with pytest.raises(ValueError, match="is_staff"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpassword",
                is_staff=False,
            )


@pytest.mark.django_db
class TestUserDefaults:
    def test_default_role_is_customer(self):
        user = User.objects.create_user(
            email="customer@example.com",
            password="testpassword",
        )

        assert user.role == User.Role.CUSTOMER

    def test_default_name_is_blank(self):
        user = User.objects.create_user(
            email="noname@example.com",
            password="testpassword",
        )

        assert user.name == ""


@pytest.mark.django_db
class TestRoleProperties:
    def test_is_organizer(self):
        user = User.objects.create_user(
            email="org@example.com",
            password="testpassword",
            role=User.Role.ORGANIZER,
        )

        assert user.is_organizer
        assert not user.is_customer
        assert not user.is_receptionist

    def test_is_customer(self):
        user = User.objects.create_user(
            email="cli@example.com",
            password="testpassword",
            role=User.Role.CUSTOMER,
        )

        assert user.is_customer
        assert not user.is_organizer
        assert not user.is_receptionist

    def test_is_receptionist(self):
        user = User.objects.create_user(
            email="rec@example.com",
            password="testpassword",
            role=User.Role.RECEPTIONIST,
        )

        assert user.is_receptionist
        assert not user.is_organizer
        assert not user.is_customer


@pytest.mark.django_db
class TestUserStr:
    def test_str_returns_email(self):
        user = User.objects.create_user(
            email="str@example.com",
            password="testpassword",
        )

        assert str(user) == "str@example.com"
