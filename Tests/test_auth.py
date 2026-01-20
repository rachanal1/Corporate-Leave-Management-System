def test_home(client):
    res = client.get("/")
    assert res.status_code == 200


def test_register_employee(client):

    # Create manager first
    client.post(
        "/register",
        json={
            "username": "manager_auth",
            "password": "Strong@123",
            "role": "manager"
        }
    )

    # Then create employee
    res = client.post(
        "/register",
        json={
            "username": "employee_test_1",
            "password": "Strong@123",
            "role": "employee"
        }
    )

    assert res.status_code == 200



def test_login_employee(client):

    # Create manager first
    client.post(
        "/register",
        json={
            "username": "manager_login",
            "password": "Strong@123",
            "role": "manager"
        }
    )

    # Create employee
    client.post(
        "/register",
        json={
            "username": "employee1",
            "password": "Strong@123",
            "role": "employee"
        }
    )

    # Login
    res = client.post(
        "/login",
        json={
            "username": "employee1",
            "password": "Strong@123"
        }
    )

    assert res.status_code == 200
    assert "role" in res.json()


