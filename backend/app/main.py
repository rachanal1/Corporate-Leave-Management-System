import re
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
from app.database import Base, engine, SessionLocal
from app.models import User, Leave
from app.schema import UserCreate, Login, LeaveCreate, RejectLeave
from app.auth import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()
TOTAL_LEAVES_PER_YEAR = 20
MAX_EMPLOYEES_PER_MANAGER = 12


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "API running"}

def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )


# REGISTER
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    if not is_strong_password(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters and include uppercase, lowercase, number, and special character"
        )

    if not user.role:
        raise HTTPException(status_code=400, detail="Role is required")

    if user.role not in ["employee", "manager", "hr"]:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role
    )

    # ✅ AUTO-ASSIGN MANAGER FOR EMPLOYEE
    if user.role == "employee":
        managers = db.query(User).filter(User.role == "manager").all()

        assigned = False
        for manager in managers:
            count = db.query(User).filter(User.manager_id == manager.id).count()
            if count < MAX_EMPLOYEES_PER_MANAGER:
                new_user.manager_id = manager.id
                assigned = True
                break

        if not assigned:
            raise HTTPException(
                status_code=400,
                detail="No manager available for assignment"
            )


    db.add(new_user)
    db.commit()
    return {"message": "Registered successfully"}


# LOGIN
@app.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    return {"id": user.id, "role": user.role}

# APPLY LEAVE
@app.post("/apply_leave/{user_id}")
def apply_leave(user_id: int, leave: LeaveCreate, db: Session = Depends(get_db)):
    new_leave = Leave(
        user_id=user_id,
        from_date=leave.from_date,
        to_date=leave.to_date,
        reason=leave.reason,
        status="Pending"
    )
    db.add(new_leave)
    db.commit()
    return {"message": "Leave applied successfully"}

# GET ALL LEAVES (manager)
@app.get("/leaves")
def get_all_leaves(db: Session = Depends(get_db)):
    results = (
        db.query(
            Leave.id,
            Leave.from_date,
            Leave.to_date,
            Leave.reason,
            Leave.status,
            Leave.rejection_reason,
            User.username,
            User.role,
            Leave.user_id
        )
        .join(User, Leave.user_id == User.id)
        .all()
    )

    return [
        {
            "id": r.id,
            "from_date": r.from_date,
            "to_date": r.to_date,
            "reason": r.reason,
            "status": r.status,
            "rejection_reason": r.rejection_reason,
            "username": r.username,
            "role": r.role,
            "user_id": r.user_id
        }
        for r in results
    ]


# MY LEAVES
@app.get("/my_leaves/{user_id}")
def my_leaves(user_id: int, db: Session = Depends(get_db)):
    return db.query(Leave).filter(Leave.user_id == user_id).all()

# APPROVE
@app.post("/approve/{leave_id}/{approver_id}")
def approve_leave(
    leave_id: int,
    approver_id: int,
    db: Session = Depends(get_db)
):

    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    approver = db.query(User).filter(User.id == approver_id).first()
    applicant = db.query(User).filter(User.id == leave.user_id).first()
    # ✅ Manager can approve ONLY their team
    if approver.role == "manager":
        if applicant.manager_id != approver.id:
            raise HTTPException(
            status_code=403,
            detail="You are not responsible for this employee"
            )

    if not leave or not approver or not applicant:
        raise HTTPException(status_code=404, detail="Invalid request")

    if leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Leave already processed")

    # ---------------- LEAVE BALANCE CHECK ----------------

    # Calculate requested leave days
    requested_days = (leave.to_date - leave.from_date).days + 1

    # Get already approved leaves for the applicant
    approved_leaves = db.query(Leave).filter(
        Leave.user_id == applicant.id,
        Leave.status == "Approved"
    ).all()

    used_days = sum(
        (l.to_date - l.from_date).days + 1
        for l in approved_leaves
        )

    remaining_days = TOTAL_LEAVES_PER_YEAR - used_days

    if requested_days > remaining_days:
        raise HTTPException(
        status_code=400,
        detail="Insufficient leave balance"
        )

    # ----------------------------------------------------

    # ❌ Cannot approve own leave
    if approver.id == applicant.id:
        raise HTTPException(status_code=403, detail="Cannot approve your own leave")

    # ✅ Manager → Employee
    if approver.role == "manager" and applicant.role == "employee":
        leave.status = "Approved"

    # ✅ HR → Manager
    elif approver.role == "hr" and applicant.role == "manager":
        leave.status = "Approved"

    else:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to approve this leave"
        )

    db.commit()
    return {"message": "Leave approved"}


# REJECT
@app.post("/reject/{leave_id}/{approver_id}")
def reject_leave(
    leave_id: int,
    approver_id: int,
    data: RejectLeave,
    db: Session = Depends(get_db)
):

    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    approver = db.query(User).filter(User.id == approver_id).first()
    applicant = db.query(User).filter(User.id == leave.user_id).first()
    # ✅ Manager can reject ONLY their team
    if approver.role == "manager":
        if applicant.manager_id != approver.id:
            raise HTTPException(
            status_code=403,
            detail="You are not responsible for this employee"
            )

    if not leave or not approver or not applicant:
        raise HTTPException(status_code=404, detail="Invalid request")

    if leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Leave already processed")

    if approver.id == applicant.id:
        raise HTTPException(status_code=403, detail="Cannot reject your own leave")

    if not data.reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason required")

    # Manager → Employee
    if approver.role == "manager" and applicant.role == "employee":
        pass

    # HR → Manager
    elif approver.role == "hr" and applicant.role == "manager":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to reject this leave"
        )

    leave.status = "Rejected"
    leave.rejection_reason = data.reason
    db.commit()

    return {"message": "Leave rejected"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/manager/leaves/{manager_id}")
def get_manager_leaves(manager_id: int, db: Session = Depends(get_db)):

    results = (
        db.query(
            Leave.id,
            Leave.from_date,
            Leave.to_date,
            Leave.reason,
            Leave.status,
            Leave.rejection_reason,
            User.username,
            User.role,
            Leave.user_id
        )
        .join(User, Leave.user_id == User.id)
        .filter(User.manager_id == manager_id)
        .all()
    )

    return [
        {
            "id": r.id,
            "from_date": r.from_date,
            "to_date": r.to_date,
            "reason": r.reason,
            "status": r.status,
            "rejection_reason": r.rejection_reason,
            "username": r.username,
            "role": r.role,
            "user_id": r.user_id
        }
        for r in results
    ]


@app.get("/manager/stats/{manager_id}")
def manager_stats(manager_id: int, db: Session = Depends(get_db)):

    team = db.query(User).filter(User.manager_id == manager_id).all()
    team_ids = [u.id for u in team]

    on_leave = db.query(Leave).filter(
        Leave.user_id.in_(team_ids),
        Leave.status == "Approved"
    ).count()

    pending = db.query(Leave).filter(
        Leave.user_id.in_(team_ids),
        Leave.status == "Pending"
    ).count()

    return {
        "team_size": len(team),
        "on_leave": on_leave,
        "pending": pending
    }


@app.get("/hr/stats/users")
def total_users(db: Session = Depends(get_db)):
    return {"total_users": db.query(User).count()}

@app.get("/hr/stats/on-leave")
def users_on_leave(db: Session = Depends(get_db)):
    count = db.query(Leave).filter(Leave.status == "Approved").count()
    return {"on_leave": count}

@app.get("/hr/manager-team/{manager_id}")
def get_manager_team(manager_id: int, db: Session = Depends(get_db)):

    results = (
        db.query(
            User.username,
            Leave.from_date,
            Leave.to_date,
            Leave.reason,
            Leave.status,
            Leave.rejection_reason
        )
        .join(Leave, Leave.user_id == User.id, isouter=True)
        .filter(User.manager_id == manager_id)
        .all()
    )

    return [
        {
            "username": r.username,
            "from_date": r.from_date,
            "to_date": r.to_date,
            "reason": r.reason,
            "status": r.status,
            "rejection_reason": r.rejection_reason
        }
        for r in results
    ]



@app.get("/leave-balance/{user_id}")
def get_leave_balance(user_id: int, db: Session = Depends(get_db)):
    current_year = date.today().year

    approved_leaves = db.query(Leave).filter(
        Leave.user_id == user_id,
        Leave.status == "Approved"
    ).all()

    used_days = 0
    for leave in approved_leaves:
        if leave.from_date.year == current_year:
            used_days += (leave.to_date - leave.from_date).days + 1

    remaining = TOTAL_LEAVES_PER_YEAR - used_days

    return {
        "total": TOTAL_LEAVES_PER_YEAR,
        "used": used_days,
        "remaining": max(remaining, 0)
    }

# DELETE
@app.delete("/delete/{leave_id}")
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(Leave).get(leave_id)
    db.delete(leave)
    db.commit()
    return {"message": "Deleted"}
