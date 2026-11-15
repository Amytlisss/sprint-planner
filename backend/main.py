from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from database import engine, get_db, Base, SessionLocal
from models import Member, Absence, Task, Sprint, Priority
from schemas import (
    MemberCreate, AbsenceCreate, TaskCreate, SprintCreate, SprintResult
)
from algorithm import calculate_capacity, select_tasks_for_sprint

# Создаём таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sprint Planner API")

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== ЭНДПОИНТЫ: КОМАНДА =====

@app.post("/members", response_model=dict)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    db_member = Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return {"id": db_member.id, "name": db_member.name, "role": db_member.role}


@app.get("/members", response_model=List[dict])
def get_members(db: Session = Depends(get_db)):
    return [
        {"id": m.id, "name": m.name, "role": m.role, "hours_per_day": m.hours_per_day}
        for m in db.query(Member).all()
    ]


# ===== ЭНДПОИНТЫ: ОТСУТСТВИЯ =====

@app.post("/absences", response_model=dict)
def create_absence(absence: AbsenceCreate, db: Session = Depends(get_db)):
    db_absence = Absence(**absence.model_dump())
    db.add(db_absence)
    db.commit()
    db.refresh(db_absence)
    return {"id": db_absence.id, "member_id": db_absence.member_id}


# ===== ЭНДПОИНТЫ: ЗАДАЧИ =====

@app.post("/tasks", response_model=dict)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"id": db_task.id, "title": db_task.title, "priority": db_task.priority}


@app.get("/tasks", response_model=List[dict])
def get_tasks(db: Session = Depends(get_db)):
    return [
        {
            "id": t.id,
            "title": t.title,
            "estimated_hours": t.estimated_hours,
            "priority": t.priority,
        }
        for t in db.query(Task).all()
    ]


# ===== ГЛАВНЫЙ ЭНДПОИНТ: РАСЧЁТ СПРИНТА =====

@app.post("/sprints/calculate", response_model=SprintResult)
def calculate_sprint(sprint_data: SprintCreate, db: Session = Depends(get_db)):
    """
    Главная функция: рассчитывает ёмкость команды и подбирает задачи.
    """
    # 1. Получаем всех сотрудников и их отсутствия
    members = db.query(Member).all()
    absences = db.query(Absence).all()
    tasks = db.query(Task).filter(Task.sprint_id.is_(None)).all()
    
    if not members:
        raise HTTPException(status_code=400, detail="Добавьте хотя бы одного сотрудника")
    if not tasks:
        raise HTTPException(status_code=400, detail="Добавьте хотя бы одну задачу")
    
    # 2. Рассчитываем ёмкость
    capacity = calculate_capacity(
        members, absences, sprint_data.start_date, sprint_data.end_date, sprint_data.focus_factor
    )
    
    # 3. Подбираем задачи
    selected = select_tasks_for_sprint(tasks, capacity)
    selected_ids = [t.id for t in selected]
    all_ids = [t.id for t in tasks]
    skipped_ids = [tid for tid in all_ids if tid not in selected_ids]
    
    planned_hours = sum(t.estimated_hours for t in selected)
    
    # 4. Создаём спринт в БД
    db_sprint = Sprint(
        name=sprint_data.name,
        start_date=sprint_data.start_date,
        end_date=sprint_data.end_date,
        total_capacity_hours=capacity,
        planned_hours=planned_hours,
    )
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    
    # 5. Привязываем выбранные задачи к спринту
    for task_id in selected_ids:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.sprint_id = db_sprint.id
    db.commit()
    
    return SprintResult(
        sprint_id=db_sprint.id,
        total_capacity_hours=capacity,
        planned_hours=planned_hours,
        selected_tasks=selected_ids,
        skipped_tasks=skipped_ids,
    )


@app.get("/sprints", response_model=List[dict])
def get_sprints(db: Session = Depends(get_db)):
    return [
        {
            "id": s.id,
            "name": s.name,
            "total_capacity_hours": s.total_capacity_hours,
            "planned_hours": s.planned_hours,
        }
        for s in db.query(Sprint).all()
    ]

def seed_data():
    """Автоматически заполняет БД тестовыми данными при первом запуске."""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже данные
        if db.query(Member).count() == 0:
            # Добавляем сотрудников
            members = [
                Member(name="Вася", role="Backend Dev", hours_per_day=8),
                Member(name="Петя", role="Frontend Dev", hours_per_day=6),
                Member(name="Маша", role="QA Engineer", hours_per_day=8),
            ]
            db.add_all(members)
            db.commit()
            
            # Добавляем задачи
            tasks = [
                Task(title="Написать API", description="Реализовать REST API", estimated_hours=40, priority=Priority.HIGH),
                Task(title="Написать тесты", description="Unit-тесты для алгоритма", estimated_hours=20, priority=Priority.MEDIUM),
                Task(title="Обновить документацию", description="Обновить README", estimated_hours=10, priority=Priority.LOW),
                Task(title="Настроить CI/CD", description="GitLab CI пайплайн", estimated_hours=15, priority=Priority.HIGH),
                Task(title="Деплой на сервер", description="Настроить Docker", estimated_hours=12, priority=Priority.MEDIUM),
            ]
            db.add_all(tasks)
            db.commit()
            
            print("✅ База данных заполнена тестовыми данными")
        else:
            print("ℹ️ База данных уже содержит данные, пропускаем заполнение")
    finally:
        db.close()


# Вызываем функцию при запуске
seed_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)