import uuid

import pytest
import requests

SITE = "https://quickpizza.grafana.com"


def pytest_configure(config):
    """Keep login-token fixture arguments out of failure reports by default."""
    if config.option.tbstyle == "auto":
        config.option.tbstyle = "short"


class QuickPizza(requests.Session):
    """Keep load-balancer cookies and accept API paths with a finite timeout."""

    def request(self, method, url, *args, **kwargs):
        kwargs.setdefault("timeout", 30)
        return super().request(method, SITE + url, *args, **kwargs)


@pytest.fixture(scope="session")
def api():
    with QuickPizza() as session:
        yield session


def log_in_new_user(api):
    """Create a unique disposable user and return its own login token."""
    user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201, res.text
    assert res.json()["username"] == user["username"]
    res = api.post("/api/users/token/login", json=user)
    assert res.status_code == 200, res.text
    token = res.json()["token"]
    assert isinstance(token, str) and token
    return {"Authorization": "token " + token}


@pytest.fixture
def auth(api):
    return log_in_new_user(api)


@pytest.fixture
def other_auth(api):
    return log_in_new_user(api)


@pytest.fixture
def pizza_id(api, auth):
    res = api.post("/api/pizza", json={}, headers=auth)
    assert res.status_code == 200, res.text
    return res.json()["pizza"]["id"]


@pytest.fixture
def create_rating(api, auth):
    """Track this test's ratings and remove them even if an assertion fails."""
    made_ids = []

    def create(body):
        res = api.post("/api/ratings", json=body, headers=auth)
        if res.status_code == 201:
            made_ids.append(res.json()["id"])
        return res

    yield create
    for rating_id in made_ids:
        res = api.delete(f"/api/ratings/{rating_id}", headers=auth)
        if res.status_code == 400:
            # DELETE reports 400 when the delete test already removed this rating.
            assert res.json() == {"error": f"rating ID {rating_id} not found"}
        else:
            assert res.status_code in (204, 404), res.text


@pytest.fixture
def rating(create_rating, pizza_id):
    res = create_rating({"pizza_id": pizza_id, "stars": 3})
    assert res.status_code == 201, res.text
    return res.json()
