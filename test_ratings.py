# Creating a rating returns its integer id, chosen stars and pizza id.
def test_create_rating(create_rating, pizza_id):
    res = create_rating({"pizza_id": pizza_id, "stars": 5})
    assert res.status_code == 201
    body = res.json()
    assert body["stars"] == 5
    assert body["pizza_id"] == pizza_id
    assert type(body["id"]) is int


# The owner can read back exactly the rating created for this test.
def test_read_rating(api, auth, rating):
    res = api.get(f"/api/ratings/{rating['id']}", headers=auth)
    assert res.status_code == 200
    assert res.json() == rating


# Updating a rating returns its new stars and preserves its identity.
def test_update_rating(api, auth, rating):
    res = api.put(f"/api/ratings/{rating['id']}", json={"stars": 4}, headers=auth)
    assert res.status_code == 200
    assert res.json() == {**rating, "stars": 4}


# Deleting a rating returns no body and makes a subsequent read return 404.
def test_delete_rating(api, auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.delete(path, headers=auth)
    assert res.status_code == 204
    assert res.content == b""
    res = api.get(path, headers=auth)
    assert res.status_code == 404
