const API = "http://127.0.0.1:8000";

/* ================= INIT ================= */
function initDashboard() {
    const role = localStorage.getItem("role");

    // Hide all sections first
    ["applySection", "approveSection", "myLeaveSection", "hrSection"]
        .forEach(id => document.getElementById(id).classList.add("hidden"));

    // Hide all buttons first
    document.getElementById("applyBtn").style.display = "none";
    document.getElementById("myLeavesBtn").style.display = "none";
    document.getElementById("approveBtn").style.display = "none";
    document.getElementById("hrBtn").style.display = "none";
    document.getElementById("managerDashBtn").style.display = "none";

    // ================= EMPLOYEE =================
    if (role === "employee") {
        document.getElementById("applyBtn").style.display = "inline-block";
        document.getElementById("myLeavesBtn").style.display = "inline-block";
        showApply();
    }

    // ================= MANAGER =================
    if (role === "manager") {
        document.getElementById("applyBtn").style.display = "inline-block";
        document.getElementById("myLeavesBtn").style.display = "inline-block";
        document.getElementById("approveBtn").style.display = "inline-block";
        document.getElementById("managerDashBtn").style.display = "inline-block";
        showApply(); // 👈 default page for manager
    }

    // ================= HR =================
    if (role === "hr") {
        document.getElementById("hrBtn").style.display = "inline-block";
        showHR();
    }
}

/* ================= LOGIN ================= */
function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const msg = document.getElementById("msg");

    msg.innerText = "";

    fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
    })
    .then(data => {
        localStorage.setItem("user_id", data.id);
        localStorage.setItem("role", data.role);
        window.location.href = "dashboard.html";
    })
    .catch(() => {
        msg.style.color = "red";
        msg.innerText = "Invalid login credentials";
    });
}

/* ================= REGISTER ================= */
function register() {
    const username = document.getElementById("reg_username").value;
    const password = document.getElementById("reg_password").value;
    const role = document.getElementById("reg_role").value;
    const msg = document.getElementById("reg_msg");
    if (!role) {
    msg.style.color = "red";
    msg.innerText = "Please select a role";
    return;
    }

    msg.innerText = "";

    fetch(`${API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role })
    })
    .then(async res => {
    const data = await res.json();
    if (!res.ok) throw data;
    msg.style.color = "green";
    msg.innerText = "Registration successful. Please login.";
})
.catch(err => {
    msg.style.color = "red";
    msg.innerText = err.detail || "Registration failed";
});
}

/* ================= SECTION TOGGLES ================= */
function showApply() {
    document.getElementById("applySection").classList.remove("hidden");
    document.getElementById("approveSection").classList.add("hidden");
    document.getElementById("myLeaveSection").classList.add("hidden");
    document.getElementById("hrSection").classList.add("hidden");
    document.getElementById("managerSection").classList.add("hidden");

    loadLeaveBalance();
}


function showApprove() {
    document.getElementById("approveSection").classList.remove("hidden");
    document.getElementById("applySection").classList.add("hidden");
    document.getElementById("myLeaveSection").classList.add("hidden");
    document.getElementById("hrSection").classList.add("hidden");
    document.getElementById("managerSection").classList.add("hidden");
    loadLeaves();
}

function showMyLeaves() {
    document.getElementById("applySection").classList.add("hidden");
    document.getElementById("approveSection").classList.add("hidden");
    document.getElementById("myLeaveSection").classList.remove("hidden");
    document.getElementById("hrSection").classList.add("hidden");
    document.getElementById("managerSection").classList.add("hidden");
    loadMyLeaves();
}

function showHR() {
    ["applySection", "approveSection", "myLeaveSection"].forEach(id => {
        document.getElementById(id).classList.add("hidden");
    });

    document.getElementById("hrSection").classList.remove("hidden");
    loadHRData();
}

function showManagerDashboard() {
    ["applySection", "approveSection", "myLeaveSection", "hrSection"]
        .forEach(id => document.getElementById(id).classList.add("hidden"));

    document.getElementById("managerSection").classList.remove("hidden");
    loadManagerStats();
}


/* ================= APPLY LEAVE ================= */
function applyLeave() {
    const userId = localStorage.getItem("user_id");
    const from_date = document.getElementById("from_date").value;
    const to_date = document.getElementById("to_date").value;
    const reason = document.getElementById("reason").value;
    const msg = document.getElementById("applyMsg");

    msg.innerText = "";

    fetch(`${API}/apply_leave/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from_date, to_date, reason })
    })
    .then(res => {
        if (!res.ok) throw new Error();
        msg.style.color = "green";
        msg.innerText = "Leave applied successfully";
    })
    .catch(() => {
        msg.style.color = "red";
        msg.innerText = "Failed to apply leave";
    });
}

/* ================= LOAD MY LEAVES ================= */
function loadMyLeaves() {
    const userId = localStorage.getItem("user_id");

    fetch(`${API}/my_leaves/${userId}`)
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("myLeaveTable");
        table.innerHTML = "";

        if (data.length === 0) {
            table.innerHTML = `<tr><td colspan="4">No leaves applied</td></tr>`;
            return;
        }

        data.forEach(l => {
            table.innerHTML += `
                <tr>
                    <td>${l.from_date}</td>
                    <td>${l.to_date}</td>
                    <td>${l.reason}</td>
                    <td>
                        ${l.status}
                        ${l.status === "Rejected"
                            ? `<br><small>(${l.rejection_reason})</small>`
                            : ""}
                    </td>
                </tr>
            `;
        });
    });
}

/* ================= LOAD ALL LEAVES (MANAGER) ================= */
function loadLeaves() {
    const currentUserId = localStorage.getItem("user_id");
    const role = localStorage.getItem("role");
    const userId = localStorage.getItem("user_id");

    const url =
        role === "manager"
            ? `${API}/manager/leaves/${userId}`
            : `${API}/leaves`;

    fetch(url)
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("leaveTable");
        table.innerHTML = "";

        if (data.length === 0) {
            table.innerHTML = `<tr><td colspan="7">No leave records</td></tr>`;
            return;
        }

        data.forEach(l => {
            const canApprove =
            l.status === "Pending" &&
            (
                (role === "manager" && l.role === "employee") ||
                (role === "hr" && l.role === "manager")
            ) &&
            l.user_id != currentUserId;


            const canDelete =
                l.status !== "Pending" &&
                (role === "manager" || l.user_id == currentUserId);

            table.innerHTML += `
                <tr>
                    <td>${l.username} (${l.role})</td>
                    <td>${l.from_date}</td>
                    <td>${l.to_date}</td>
                    <td>${l.reason}</td>
                    <td>
                        ${l.status}
                        ${l.status === "Rejected" && l.rejection_reason
                            ? `<br><small>(${l.rejection_reason})</small>`
                            : ""}
                    </td>
                    <td>
                        ${canApprove
                            ? `
                                <button onclick="approve(${l.id})">Approve</button>
                                <button onclick="reject(${l.id})">Reject</button>
                              `
                            : "-"}
                    </td>
                    <td>
                        ${canDelete
                            ? `<button onclick="deleteLeave(${l.id})">Delete</button>`
                            : "-"}
                    </td>
                </tr>
            `;
        });
    });
}

function loadLeaveBalance() {
    const userId = localStorage.getItem("user_id");

    fetch(`${API}/leave-balance/${userId}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("totalLeaves").innerText = data.total;
            document.getElementById("usedLeaves").innerText = data.used;
            document.getElementById("remainingLeaves").innerText = data.remaining;
        });
}


/* ================= APPROVE / REJECT ================= */
function approve(id) {
    const approverId = localStorage.getItem("user_id");

    fetch(`${API}/approve/${id}/${approverId}`, {
        method: "POST"
    }).then(() => {
        const role = localStorage.getItem("role");
        role === "hr" ? loadHRData() : loadLeaves();
    });
}


function reject(id) {
    const reason = prompt("Enter rejection reason:");
    if (!reason) return;

    const approverId = localStorage.getItem("user_id");

    fetch(`${API}/reject/${id}/${approverId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason })
    }).then(() => {
        const role = localStorage.getItem("role");
        role === "hr" ? loadHRData() : loadLeaves();
    });
}


/* ================= DELETE ================= */
function deleteLeave(id) {
    if (!confirm("Are you sure you want to delete this leave?")) return;

    fetch(`${API}/delete/${id}`, {
        method: "DELETE"
    }).then(() => loadLeaves());
}



function loadHRData() {
    // ✅ Local date (NOT UTC)
    const today = new Date().toLocaleDateString("en-CA");

    Promise.all([
        fetch(`${API}/users`).then(r => r.json()),
        fetch(`${API}/leaves`).then(r => r.json())
    ])
    .then(([users, leaves]) => {

        const empTable = document.getElementById("employeeTable");
        const mgrTable = document.getElementById("managerTable");

        empTable.innerHTML = "";
        mgrTable.innerHTML = "";

        const employees = users.filter(u => u.role === "employee");
        const managers  = users.filter(u => u.role === "manager");

        let employeeOnLeave = 0;
        let managerOnLeave  = 0;

        /* ================= EMPLOYEES ================= */
        employees.forEach(e => {

            const empLeaves = leaves.filter(l => {
                if (l.user_id !== e.id || l.status !== "Approved") return false;

                const from = l.from_date.split("T")[0];
                const to   = l.to_date.split("T")[0];

                return from <= today && to >= today;
            });

            const status = empLeaves.length > 0 ? "On Leave" : "Active";
            if (empLeaves.length > 0) employeeOnLeave++;

            empTable.innerHTML += `
                <tr>
                    <td>${e.username}</td>
                    <td>${status}</td>
                </tr>
            `;
        });

        /* ================= MANAGERS ================= */
        managers.forEach(m => {

            const managerLeaves = leaves.filter(l => l.user_id === m.id);

            if (managerLeaves.length === 0) {
                mgrTable.innerHTML += `
                    <tr>
                        <td>
                            <a href="#" onclick="viewManagerTeam(${m.id}, '${m.username}', this)">
                            ${m.username}
                            </a>
                        </td>
                        <td>-</td>
                        <td>-</td>    
                        <td>Active</td>
                        <td>-</td>
                    </tr>
                `;
                return;
            }

            managerLeaves.forEach(l => {
                const from = l.from_date.split("T")[0];
                const to   = l.to_date.split("T")[0];

                if (
                    l.status === "Approved" &&
                    from <= today &&
                    to >= today
                ) {
                    managerOnLeave++;
                }

                mgrTable.innerHTML += `
                    <tr>
                        <td>
                            <a href="#" onclick="viewManagerTeam(${m.id}, '${m.username}', this)">
                            ${m.username}
                            </a>
                        </td>
                        <td>${from} → ${to}</td>
                        <td>${l.reason || "-"}</td>
                        <td>${l.status}</td>
                        <td>
                            ${
                                l.status === "Pending"
                                ? `
                                    <div class="action-btns">
                                        <button onclick="approve(${l.id})">Approve</button>
                                        <button onclick="reject(${l.id})">Reject</button>
                                    </div>
                                  `
                                : "-"
                            }
                        </td>
                    </tr>
                `;
            });
        });

        /* ================= STATS ================= */
        document.getElementById("totalEmployees").innerText = employees.length;
        document.getElementById("empOnLeave").innerText      = employeeOnLeave;
        document.getElementById("totalManagers").innerText  = managers.length;
        document.getElementById("onLeave").innerText        = managerOnLeave;
    });
}

function viewManagerTeam(managerId, managerName, el) {

    const currentRow = el.closest("tr");

    // 🔁 If next row already exists → toggle
    const nextRow = currentRow.nextElementSibling;

    if (nextRow && nextRow.classList.contains("manager-team-row")) {
        nextRow.remove(); // collapse
        return;
    }

    // ❌ Close any other open manager tables
    document.querySelectorAll(".manager-team-row").forEach(r => r.remove());

    // ➕ Create expandable row
    const detailRow = document.createElement("tr");
    detailRow.className = "manager-team-row";

    const td = document.createElement("td");
    td.colSpan = 5; // match manager table columns

    td.innerHTML = `
        <strong>Employees under ${managerName}</strong>
        <div class="table-wrapper">
            <table class="inner-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Leave</th>
                        <th>Reason</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="team-${managerId}">
                    <tr><td colspan="5">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    `;

    detailRow.appendChild(td);
    currentRow.after(detailRow);

    // 🔄 Load team data
    fetch(`${API}/hr/manager-team/${managerId}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById(`team-${managerId}`);
            tbody.innerHTML = "";

            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5">No employees</td></tr>`;
                return;
            }

            data.forEach(e => {

                const leave =
                e.from_date
                    ? `${e.from_date} → ${e.to_date}`
                    : "-";

                const reason = e.reason || "-";
                const status =
                    e.status === "Rejected" && e.rejection_reason
                        ? `${e.status} (${e.rejection_reason})`
                        : e.status || "Active";

                tbody.innerHTML += `
                    <tr>
                        <td>${e.username}</td>
                        <td>${leave}</td>
                        <td>${reason}</td>
                        <td>${status}</td>
                        <td>-</td>
                    </tr>
                 `;
            });

        });
}


function loadManagerStats() {
    const managerId = localStorage.getItem("user_id");

    fetch(`${API}/manager/stats/${managerId}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("teamSize").innerText = data.team_size;
            document.getElementById("teamOnLeave").innerText = data.on_leave;
            document.getElementById("teamPending").innerText = data.pending;
        });
}


/* ================= LOGOUT ================= */
function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}