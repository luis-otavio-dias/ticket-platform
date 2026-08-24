from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test import Client

if TYPE_CHECKING:
    from django.test import Client


EXPECTED_STATUS = HTTPStatus.FOUND


@pytest.mark.django_db
def test_admin_status(client: Client) -> None:
    response = client.get("/admin/")
    assert response.status_code == EXPECTED_STATUS
