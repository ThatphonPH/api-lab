import pytest

STARS_ERROR = "number of stars must be between 1 and 5 (inclusive)"


# Base choice: integer 3 stars, an existing pizza and the owner's login token.
def test_base_choice_is_saved(create_rating, pizza_id):
    res = create_rating({"pizza_id": pizza_id, "stars": 3})
    assert res.status_code == 201
    body = res.json()
    assert body["stars"] == 3
    assert body["pizza_id"] == pizza_id
    assert type(body["id"]) is int


# C1: integers below 1 and above 5 are refused with the stars-range error.
@pytest.mark.parametrize("stars", [0, 6])
def test_stars_out_of_range(create_rating, pizza_id, stars):
    res = create_rating({"pizza_id": pizza_id, "stars": stars})
    assert res.status_code == 400
    assert res.json() == {"error": STARS_ERROR}


# C2: decimal, text and missing stars are refused; all other inputs stay at base.
@pytest.mark.parametrize("fields,error", [
    ({"stars": 3.5}, "json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int"),
    ({"stars": "3"}, "json: cannot unmarshal string into Go struct field Rating.stars of type int"),
    ({}, STARS_ERROR),
], ids=["decimal", "text", "missing"])
def test_invalid_stars_type(create_rating, pizza_id, fields, error):
    res = create_rating({"pizza_id": pizza_id, **fields})
    assert res.status_code == 400
    assert res.json() == {"error": error}


# C3: a nonexistent pizza is refused even with valid stars and the owner's token.
def test_nonexistent_pizza_is_refused(create_rating):
    res = create_rating({"pizza_id": 999999999, "stars": 3})
    assert res.status_code == 400
    assert res.json() == {"error": "pizza ID 999999999 not found"}


# C4: no token and a wrong-length token are refused with the authentication error.
@pytest.mark.parametrize("headers", [{}, {"Authorization": "token short"}], ids=["none", "wrong-length"])
def test_invalid_token_is_refused(api, pizza_id, headers):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=headers)
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
