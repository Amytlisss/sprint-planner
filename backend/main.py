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

# Создаем таблицы при запуске приложения
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sprint Planner API")

# Настройка CORS для запросов с фронтенда
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
    """Создание нового сотрудника команды."""
    db_member = Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return {"id": db_member.id, "name": db_member.name, "role": db_member.role}


@app.get("/members", response_model=List[dict])
def get_members(include_inactive: bool = False, db: Session = Depends(get_db)):
    """Получение списка сотрудников. По умолчанию только активные."""
    query = db.query(Member)
    if not include_inactive:
        query = query.filter(Member.is_active == True)
    
    return [
        {"id": m.id, "name": m.name, "role": m.role, "hours_per_day": m.hours_per_day, "is_active": m.is_active}
        for m in query.all()
    ]


@app.put("/members/{member_id}", response_model=dict)
def update_member(member_id: int, member: MemberCreate, db: Session = Depends(get_db)):
    """Редактирование данных сотрудника."""
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    db_member.name = member.name
    db_member.role = member.role
    db_member.hours_per_day = member.hours_per_day
    db.commit()
    db.refresh(db_member)
    
    return {"id": db_member.id, "name": db_member.name, "role": db_member.role}


@app.delete("/members/{member_id}", response_model=dict)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """Мягкое удаление сотрудника (помечается как неактивный)."""
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    db_member.is_active = False
    db.commit()
    return {"message": "Сотрудник деактивирован"}


@app.post("/members/{member_id}/reactivate", response_model=dict)
def reactivate_member(member_id: int, db: Session = Depends(get_db)):
    """Восстановление деактивированного сотрудника."""
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    db_member.is_active = True
    db.commit()
    return {"message": "Сотрудник восстановлен"}


# ===== ЭНДПОИНТЫ: ЗАДАЧИ =====

@app.post("/tasks", response_model=dict)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Добавление новой задачи в бэклог."""
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"id": db_task.id, "title": db_task.title, "priority": db_task.priority}


@app.get("/tasks", response_model=List[dict])
def get_tasks(include_inactive: bool = False, db: Session = Depends(get_db)):
    """Получение списка задач. По умолчанию только активные."""
    query = db.query(Task)
    if not include_inactive:
        query = query.filter(Task.is_active == True)
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "estimated_hours": t.estimated_hours,
            "priority": t.priority,
            "is_active": t.is_active,
        }
        for t in query.all()
    ]


@app.put("/tasks/{task_id}", response_model=dict)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    """Редактирование задачи."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.estimated_hours = task.estimated_hours
    db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)
    
    return {"id": db_task.id, "title": db_task.title, "priority": db_task.priority}


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Мягкое удаление задачи (помечается как неактивная)."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db_task.is_active = False
    db.commit()
    return {"message": "Задача деактивирована"}


@app.post("/tasks/{task_id}/reactivate", response_model=dict)
def reactivate_task(task_id: int, db: Session = Depends(get_db)):
    """Восстановление деактивированной задачи."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db_task.is_active = True
    db.commit()
    return {"message": "Задача восстановлена"}

# ===== ЭНДПОИНТЫ: ОТСУТСТВИЯ =====

@app.get("/absences", response_model=List[dict])
def get_absences(db: Session = Depends(get_db)):
    """Получение списка всех отсутствий сотрудников."""
    return [
        {
            "id": a.id,
            "member_id": a.member_id,
            "member_name": a.member.name,
            "start_date": a.start_date.isoformat(),
            "end_date": a.end_date.isoformat(),
            "reason": a.reason,
        }
        for a in db.query(Absence).all()
    ]


@app.post("/absences", response_model=dict)
def create_absence(absence: AbsenceCreate, db: Session = Depends(get_db)):
    """Добавление отсутствия (отпуск, больничный, праздник)."""
    db_absence = Absence(**absence.model_dump())
    db.add(db_absence)
    db.commit()
    db.refresh(db_absence)
    return {"id": db_absence.id, "member_id": db_absence.member_id}


@app.delete("/absences/{absence_id}", response_model=dict)
def delete_absence(absence_id: int, db: Session = Depends(get_db)):
    """Удаление записи об отсутствии."""
    absence = db.query(Absence).filter(Absence.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=404, detail="Отсутствие не найдено")
    db.delete(absence)
    db.commit()
    return {"message": "Отсутствие удалено"}


# ===== ГЛАВНЫЙ ЭНДПОИНТ: РАСЧЕТ СПРИНТА =====

@app.post("/sprints/calculate", response_model=SprintResult)
def calculate_sprint(sprint_data: SprintCreate, db: Session = Depends(get_db)):
    """
    Расчет доступной емкости команды и подбор задач для спринта.
    """
    # Получаем только активных сотрудников и активные задачи
    members = db.query(Member).filter(Member.is_active == True).all()
    absences = db.query(Absence).all()
    tasks = db.query(Task).filter(Task.is_active == True).all()
    
    if not members:
        raise HTTPException(status_code=400, detail="Добавьте хотя бы одного сотрудника")
    if not tasks:
        raise HTTPException(status_code=400, detail="Добавьте хотя бы одну задачу")
    
    # Расчет доступной емкости команды
    capacity = calculate_capacity(
        members, absences, sprint_data.start_date, sprint_data.end_date, sprint_data.focus_factor
    )
    
    # Подбор задач по приоритету (жадный алгоритм)
    selected = select_tasks_for_sprint(tasks, capacity)
    selected_ids = [t.id for t in selected]
    all_ids = [t.id for t in tasks]
    skipped_ids = [tid for tid in all_ids if tid not in selected_ids]
    
    planned_hours = sum(t.estimated_hours for t in selected)
    
    # Сохранение результатов спринта в БД
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
    
    return SprintResult(
        sprint_id=db_sprint.id,
        total_capacity_hours=capacity,
        planned_hours=planned_hours,
        selected_tasks=selected_ids,
        skipped_tasks=skipped_ids,
    )

@app.get("/sprints", response_model=List[dict])
def get_sprints(db: Session = Depends(get_db)):
    """Получение списка всех рассчитанных спринтов."""
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
    """Заполнение БД тестовыми данными при первом запуске."""
    db = SessionLocal()
    try:
        if db.query(Member).count() == 0:
            members = [
                Member(name="Вася", role="Backend Dev", hours_per_day=8),
                Member(name="Петя", role="Frontend Dev", hours_per_day=6),
                Member(name="Маша", role="QA Engineer", hours_per_day=8),
            ]
            db.add_all(members)
            db.commit()
            
            tasks = [
                Task(title="Написать API", description="Реализовать REST API", estimated_hours=40, priority=Priority.HIGH),
                Task(title="Написать тесты", description="Unit-тесты для алгоритма", estimated_hours=20, priority=Priority.MEDIUM),
                Task(title="Обновить документацию", description="Обновить README", estimated_hours=10, priority=Priority.LOW),
                Task(title="Настроить CI/CD", description="GitLab CI пайплайн", estimated_hours=15, priority=Priority.HIGH),
                Task(title="Деплой на сервер", description="Настроить Docker", estimated_hours=12, priority=Priority.MEDIUM),
            ]
            db.add_all(tasks)
            db.commit()
            
            print("База данных заполнена тестовыми данными")
        else:
            print("База данных уже содержит данные, пропускаем заполнение")
    finally:
        db.close()

# ===== ЭНДПОИНТЫ: РЕДАКТИРОВАНИЕ И УДАЛЕНИЕ СОТРУДНИКОВ =====

@app.put("/members/{member_id}", response_model=dict)
def update_member(member_id: int, member: MemberCreate, db: Session = Depends(get_db)):
    """Редактирование данных сотрудника."""
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    db_member.name = member.name
    db_member.role = member.role
    db_member.hours_per_day = member.hours_per_day
    db.commit()
    db.refresh(db_member)
    
    return {"id": db_member.id, "name": db_member.name, "role": db_member.role}


@app.delete("/members/{member_id}", response_model=dict)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """Удаление сотрудника."""
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    db.delete(db_member)
    db.commit()
    return {"message": "Сотрудник удален"}


# ===== ЭНДПОИНТЫ: РЕДАКТИРОВАНИЕ И УДАЛЕНИЕ ЗАДАЧ =====

@app.put("/tasks/{task_id}", response_model=dict)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    """Редактирование задачи."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.estimated_hours = task.estimated_hours
    db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)
    
    return {"id": db_task.id, "title": db_task.title, "priority": db_task.priority}


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удаление задачи."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Задача удалена"}

seed_data()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)