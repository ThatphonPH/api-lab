import pytest


# Boundary updates save 1 and 5 stars; rejected 0 and 6 leave stored data unchanged.
@pytest.mark.parametrize("stars,expected_status", [(0, 400), (1, 200), (5, 200), (6, 400)])
def test_update_stars_boundaries(api, auth, rating, stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == expected_status
    expected = {**rating, "stars": stars} if expected_status == 200 else rating
    if expected_status == 200:
        assert res.json() == expected
    else:
        assert res.json() == {"error": "number of stars must be between 1 and 5 (inclusive)"}
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == expected
