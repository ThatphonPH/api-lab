import pytest


# Excluding zero, one or two tools still returns a pizza using an allowed tool.
@pytest.mark.parametrize("excluded", [[], ["Knife"], ["Scissors"], ["Knife", "Scissors"]],
                         ids=["zero", "one-knife", "one-scissors", "two"])
def test_excluded_tool_is_not_used(api, auth, excluded):
    res = api.post("/api/pizza", json={"excludedTools": excluded}, headers=auth)
    assert res.status_code == 200
    assert res.json()["pizza"]["tool"] in {"Knife", "Pizza cutter", "Scissors"} - set(excluded)


# An impossible restriction should return a client error with a useful JSON message.
@pytest.mark.xfail(reason="Defect 1: excluding all three tools returns 500 with an empty body instead of 400 JSON", strict=True)
def test_all_tools_excluded_is_refused(api, auth):
    res = api.post("/api/pizza", json={"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}, headers=auth)
    assert res.status_code == 400
    body = res.json()
    assert isinstance(body.get("error"), str) and body["error"].strip()
