from datetime import date, timedelta
from models import Member, Absence, Task, Priority


def calculate_capacity(
    members: list[Member],
    absences: list[Absence],
    sprint_start: date,
    sprint_end: date,
    focus_factor: float = 0.8,
) -> float:
    """
    Рассчитывает реальную ёмкость команды в часах.
    
    Формула:
    1. Считаем рабочие дни в спринте (без выходных)
    2. Для каждого сотрудника вычитаем дни отсутствий
    3. Умножаем на часы в день
    4. Применяем коэффициент фокуса (по умолчанию 0.8)
    """
    total_hours = 0.0
    
    # Считаем рабочие дни (понедельник-пятница)
    working_days = 0
    current_day = sprint_start
    while current_day <= sprint_end:
        if current_day.weekday() < 5:  # 0=Пн, 4=Пт
            working_days += 1
        current_day += timedelta(days=1)
    
    # Для каждого сотрудника считаем доступные часы
    for member in members:
        absent_days = 0
        for absence in absences:
            if absence.member_id == member.id:
                # Пересечение отсутствия со спринтом
                start = max(absence.start_date, sprint_start)
                end = min(absence.end_date, sprint_end)
                if start <= end:
                    days = (end - start).days + 1
                    # Вычитаем выходные из дней отсутствия
                    for d in range(days):
                        check_date = start + timedelta(days=d)
                        if check_date.weekday() < 5:
                            absent_days += 1
        
        available_days = working_days - absent_days
        total_hours += available_days * member.hours_per_day
    
    # Применяем коэффициент фокуса
    return total_hours * focus_factor


def select_tasks_for_sprint(
    tasks: list[Task],
    capacity_hours: float,
) -> list[Task]:
    """
    Жадный алгоритм выбора задач для спринта.
    
    1. Сортирует задачи по приоритету (high -> medium -> low)
    2. Берёт задачи по порядку, пока не исчерпает ёмкость
    3. Возвращает список задач, которые "влезли" в спринт
    """
    priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
    sorted_tasks = sorted(tasks, key=lambda t: priority_order[t.priority])
    
    selected = []
    remaining_hours = capacity_hours
    
    for task in sorted_tasks:
        if task.estimated_hours <= remaining_hours:
            selected.append(task)
            remaining_hours -= task.estimated_hours
    
    return selected