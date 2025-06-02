from datetime import timedelta, date
from collections import defaultdict
from django.contrib.auth import get_user_model

def calculate_end_date(start_date: date, working_days: int, holidays: set) -> date:
    """
    Вычисляет дату окончания отпуска, пропуская праздничные дни.
    start_date: первый день отпуска
    working_days: число дней отпуска (включительно первого)
    holidays: множество объектов date, которые являются праздниками
    """
    current = start_date
    days_left = working_days - 1  # первый день учтён
    while days_left > 0:
        current += timedelta(days=1)
        if current not in holidays:
            days_left -= 1
    return current


def calculate_working_days(start_date: date, end_date: date, holidays: set) -> int:
    """
    Считает рабочие дни в диапазоне [start_date, end_date], пропуская праздничные дни.
    """
    days = 0
    current = start_date
    while current <= end_date:
        if current not in holidays:
            days += 1
        current += timedelta(days=1)
    return days


def get_bosses_dict():
    """
    Возвращает словарь вида:
      {
        "ФИО руководителя 1": [название_отдела_A, название_отдела_B, ...],
        "ФИО руководителя 2": [...],
        ...
      }
    """
    from .models import Unit, User_info

    User = get_user_model()
    temp = defaultdict(set)
    
    for boss_id, dept_desc in Unit.objects.filter(boss__isnull=False) \
                                          .values_list('boss_id', 'description'):
        if dept_desc:
            temp[boss_id].add(dept_desc)
    
    qs = User_info.objects.filter(supervisor__isnull=False, otd_number__isnull=False) \
                          .select_related('otd_number')
    for ui in qs:
        sup_id = ui.supervisor_id
        dept_desc = ui.otd_number.description
        if dept_desc:
            temp[sup_id].add(dept_desc)
    
    all_depts_list = [desc for desc in Unit.objects.values_list('description', flat=True) if desc]
    for su in User.objects.filter(is_superuser=True):
        sup_id = su.id
        existing = temp.get(sup_id, set())
        for desc in all_depts_list:
            if desc not in existing:
                temp[sup_id].add(desc)
    
    bosses_dict = {}
    for user_id, dept_set in temp.items():
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            continue
        fio = user.get_full_name()
        bosses_dict[fio] = sorted(dept_set)

    return bosses_dict