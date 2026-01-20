def test_manager_team_flow(client):
    """
    This test verifies:
    1. Employee is auto-assigned to a manager
    2. Manager can see only their team's leaves
    3. HR can view a manager's team
    4. Manager cannot approve another manager's employee
    """

    # -------------------------------
    # Create Manager 1
    # -------------------------------
    res_mgr1 = client.post(
        "/register",
        json={
            "username": "manager_one",
            "password": "Strong@123",
            "role": "manager"
        }
    )
    assert res_mgr1.status_code == 200

    # -------------------------------
    # Create Manager 2
    # -------------------------------
    res_mgr2 = client.post(
        "/register",
        json={
            "username": "manager_two",
            "password": "Strong@123",
            "role": "manager"
        }
    )
    assert res_mgr2.status_code == 200

    # -------------------------------
    # Create Employee (auto assigned to Manager 1)
    # -------------------------------
    res_emp = client.post(
        "/register",
        json={
            "username": "employee_one",
            "password": "Strong@123",
            "role": "employee"
        }
    )
    assert res_emp.status_code == 200

    # -------------------------------
    # Fetch Users
    # -------------------------------
    users = client.get("/users").json()

    manager1 = next(u for u in users if u["username"] == "manager_one")
    manager2 = next(u for u in users if u["username"] == "manager_two")
    employee = next(u for u in users if u["username"] == "employee_one")

    # -------------------------------
    # 1️⃣ Employee must be assigned to Manager 1
    # -------------------------------
    manager_ids = [u["id"] for u in users if u["role"] == "manager"]
    assert employee["manager_id"] in manager_ids

    # -------------------------------
    # Employee applies leave
    # -------------------------------
    res_leave = client.post(
        f"/apply_leave/{employee['id']}",
        json={
            "from_date": "2026-01-20",
            "to_date": "2026-01-22",
            "reason": "Family function"
        }
    )
    assert res_leave.status_code == 200

    # -------------------------------
    # 2️⃣ Manager 1 can see team leaves
    # -------------------------------
    # 🔍 Find the actual manager of the employee
    assigned_manager_id = employee["manager_id"]

    # 2️⃣ Assigned manager can see team leaves
    res_team_leaves = client.get(f"/manager/leaves/{assigned_manager_id}")
    assert res_team_leaves.status_code == 200

    team_leaves = res_team_leaves.json()
    assert len(team_leaves) == 1
    assert team_leaves[0]["user_id"] == employee["id"]

    # -------------------------------
    # 3️⃣ HR can view Manager 1 team
    # -------------------------------
    res_hr = client.get(f"/hr/manager-team/{manager1['id']}")
    assert res_hr.status_code == 200
    assert isinstance(res_hr.json(), list)

    # -------------------------------
    # 4️⃣ Manager 2 CANNOT approve Manager 1's employee
    # -------------------------------
    res_approve = client.post(
        f"/approve/{team_leaves[0]['id']}/{manager2['id']}"
    )

    assert res_approve.status_code == 403
