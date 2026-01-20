from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    from_date = Column(Date)
    to_date = Column(Date)
    reason = Column(String(255))
    status = Column(String(20), default="Pending")
    rejection_reason = Column(String(255), nullable=True)

    user = relationship("User")
