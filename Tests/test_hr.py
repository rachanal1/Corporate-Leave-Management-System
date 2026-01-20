def test_get_users(client):
    res = client.get("/users")
    assert res.status_code == 200


def test_total_users(client):
    res = client.get("/hr/stats/users")
    assert res.status_code == 200
    assert "total_users" in res.json()


def test_users_on_leave(client):
    res = client.get("/hr/stats/on-leave")
    assert res.status_code == 200
    assert "on_leave" in res.json()
