# The public practice token can read the three pizza tools.
def test_tools_are_listed(api):
    res = api.get("/api/tools", headers={"Authorization": "token abcdef0123456789"})
    assert res.status_code == 200
    assert res.json() == {"tools": ["Knife", "Pizza cutter", "Scissors"]}
