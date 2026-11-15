from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from models import Priority, SprintStatus


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    hours_per_day: int = Field(..., gt=0, le=24)


class AbsenceCreate(BaseModel):
    member_id: int
    start_date: date
    end_date: date
    reason: str = Field(default="Отпуск", max_length=100)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(default="", max_length=1000)
    estimated_hours: float = Field(..., gt=0)
    priority: Priority = Priority.MEDIUM


class SprintCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    start_date: date
    end_date: date
    focus_factor: float = Field(default=0.8, gt=0, le=1)


class SprintResult(BaseModel):
    sprint_id: int
    total_capacity_hours: float
    planned_hours: float
    selected_tasks: list[int]
    skipped_tasks: list[int]