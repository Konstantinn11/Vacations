from datetime import timedelta, date

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