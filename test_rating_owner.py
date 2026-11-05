def assert_rating_unchanged(api, auth, rating):
    res = api.get(f"/api/ratings/{rating['id']}", headers=auth)
    assert res.status_code == 200
    assert res.json() == rating


# Another user cannot read the owner's rating, which remains accessible to its owner.
def test_other_user_cannot_read_rating(api, auth, rating, other_auth):
    res = api.get(f"/api/ratings/{rating['id']}", headers=other_auth)
    print(f"Other-user GET status: {res.status_code}; body: {res.text}")
    assert 400 <= res.status_code < 500
    assert_rating_unchanged(api, auth, rating)


# Another user cannot change the owner's rating or alter any of its fields.
def test_other_user_cannot_update_rating(api, auth, rating, other_auth):
    res = api.put(f"/api/ratings/{rating['id']}", json={"stars": 5}, headers=other_auth)
    print(f"Other-user PUT status: {res.status_code}; body: {res.text}")
    assert 400 <= res.status_code < 500
    assert_rating_unchanged(api, auth, rating)


# Another user cannot delete the owner's rating, which must remain unchanged.
def test_other_user_cannot_delete_rating(api, auth, rating, other_auth):
    res = api.delete(f"/api/ratings/{rating['id']}", headers=other_auth)
    print(f"Other-user DELETE status: {res.status_code}; body: {res.text}")
    assert 400 <= res.status_code < 500
    assert_rating_unchanged(api, auth, rating)
