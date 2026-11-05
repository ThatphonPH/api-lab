# A vegetarian request returns a named pizza containing only vegetarian ingredients.
def test_vegetarian_pizza(api, auth):
    res = api.post("/api/pizza", json={"mustBeVegetarian": True}, headers=auth)
    assert res.status_code == 200
    pizza = res.json()["pizza"]
    assert pizza["name"]
    assert pizza["ingredients"]
    for ingredient in pizza["ingredients"]:
        assert ingredient["vegetarian"] is True, ingredient["name"]


# A pizza request without a token is refused with an authentication error.
def test_pizza_without_token_is_refused(api):
    res = api.post("/api/pizza", json={"mustBeVegetarian": True})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
