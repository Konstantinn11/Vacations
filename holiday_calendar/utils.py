import datetime as dt
from collections import defaultdict
from .models import Holiday
from django.utils.translation import gettext_lazy as _

month_num_str = {
    1: _('Январь'), 2: _('Февраль'), 3: _('Март'),
    4: _('Апрель'), 5: _('Май'), 6: _('Июнь'),
    7: _('Июль'), 8: _('Август'), 9: _('Сентябрь'),
    10: _('Октябрь'), 11: _('Ноябрь'), 12: _('Декабрь'),
}

def get_calendar_data(year=None):
    """
    Возвращает:
      holidays: {2025: {'Январь': [1, …], …}, …}
      special_work_days: [date(...), …]
    Если year не указан — собирает все годы.
    """
    qs = Holiday.objects.all()
    if year:
        qs = qs.filter(date__year=year)

    hols = defaultdict(lambda: defaultdict(list))
    work = []

    for rec in qs:
        y, m, d = rec.date.year, rec.date.month, rec.date.day
        if rec.is_workday:
            work.append(rec.date)
        else:
            # Приводим ленивый перевод к обычной строке для корректной сериализации в JSON
            month_name = str(month_num_str[m])
            hols[y][month_name].append(d)

    return dict(hols), work