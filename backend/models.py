from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum


class Priority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SprintStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    hours_per_day = Column(Integer, default=8)
    is_active = Column(Boolean, default=True)  # Soft delete флаг

    absences = relationship("Absence", back_populates="member")


class Absence(Base):
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, default="Отпуск")

    member = relationship("Member", back_populates="absences")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    estimated_hours = Column(Float, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    is_active = Column(Boolean, default=True)  # Soft delete флаг

    sprint = relationship("Sprint", back_populates="tasks")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_capacity_hours = Column(Float, default=0)
    planned_hours = Column(Float, default=0)
    status = Column(Enum(SprintStatus), default=SprintStatus.PLANNING)

    tasks = relationship("Task", back_populates="sprint")