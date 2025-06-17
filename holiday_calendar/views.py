from django.shortcuts import render, redirect, get_object_or_404
from .models import Holiday
from .forms import HolidayForm
from users.utils import get_bosses_dict
from users.models import Vacation
import datetime as dt

def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'no_rights.html')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@superuser_required
def holiday_list(request):
    bosses = get_bosses_dict()
    current_year = dt.datetime.now().year
    future_years = [current_year + 1, current_year + 2]
    year = int(request.GET.get('year', current_year))

    # Получаем годы, в которых есть отпуска
    years_in_vacations = set(Vacation.objects.values_list('year', flat=True))
    years_in_vacations.update([str(y) for y in future_years])
    years_range = sorted([int(y) for y in years_in_vacations], reverse=True)

    # Фильтруем праздники по году
    holidays = Holiday.objects.filter(date__year=year).order_by('date')

    context = {
        'holidays': holidays,
        'years_range': years_range,
        'selected_year': year,
        'bosses': list(bosses.keys()),
    }
    return render(request, 'holiday_calendar/holiday_list.html', context)


def holiday_edit(request, pk=None):
    bosses = get_bosses_dict()
    instance = get_object_or_404(Holiday, pk=pk) if pk else None
    form = HolidayForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('holiday_calendar:holiday_list')
    
    context = {
        'form': form,
        'bosses': list(bosses.keys()),
    }
    return render(request, 'holiday_calendar/holiday_edit.html', context)


def holiday_delete(request, pk):
    bosses = get_bosses_dict()
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        return redirect('holiday_calendar:holiday_list')
    
    context = {
        'holiday': holiday,
        'bosses': list(bosses.keys()),
    }
    return render(request, 'holiday_calendar/holiday_confirm_delete.html', context)
