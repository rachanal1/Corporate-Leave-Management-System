def test_apply_leave(client):
    res = client.post(
        "/apply_leave/1",
        json={
            "from_date": "2026-01-20",
            "to_date": "2026-01-22",
            "reason": "Family function"
        }
    )
    assert res.status_code == 200


def test_view_my_leaves(client):
    res = client.get("/my_leaves/1")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_view_all_leaves(client):
    res = client.get("/leaves")
    assert res.status_code == 200
