import uuid

import pytest


@pytest.fixture
def registered_user(api):
    user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201
    assert res.json()["username"] == user["username"]
    return user


# Registering an already used username returns the specific duplicate-name error.
def test_duplicate_username_is_refused(api, registered_user):
    res = api.post("/api/users", json=registered_user)
    assert res.status_code == 400
    assert res.json() == {"error": "username already taken"}


# An existing user cannot log in with an incorrect password.
def test_wrong_password_is_refused(api, registered_user):
    res = api.post("/api/users/token/login", json={**registered_user, "password": "Wrong-password"})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}


# An empty username is rejected before a user can be created.
def test_empty_username_is_refused(api):
    res = api.post("/api/users", json={"username": "", "password": "Pizza-2026"})
    assert res.status_code == 400
    assert res.json() == {"error": "username field is empty"}
