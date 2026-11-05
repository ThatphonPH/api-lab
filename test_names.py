# The public names endpoint returns JSON containing Margherita.
def test_names_are_listed(api):
    res = api.get("/api/names")
    assert res.status_code == 200
    assert res.headers["Content-Type"].startswith("application/json")
    assert "Margherita" in res.json()["names"]
