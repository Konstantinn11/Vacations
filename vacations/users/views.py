from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
User = get_user_model()
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import User_info, Unit, Vacation, Position
from .forms import VacationForm
import datetime as dt
from datetime import timedelta
import pandas as pd
from django.contrib import messages as msg
from calendar import monthrange
import json
from users.vacation_data import holidays, month_num_str, special_work_days, bosses, months_ru, color_cycle
from django.http import JsonResponse, Http404
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        # Получаем введенный email
        email = form.cleaned_data.get('email')

        # Проверяем, существует ли пользователь с таким email
        if not User.objects.filter(email=email).exists():
            msg.error(self.request, "Такого адреса электронной почты не существует")
            return self.form_invalid(form)

        # Сохраняем email в сессии
        self.request.session['email'] = email

        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем email из сессии
        email = self.request.session.get('email')
        if email:
            context['email'] = email
        return context
    

@login_required(login_url='/auth/login/')
def home_view(request):
    return redirect(reverse('vac_all', kwargs={'otd': 0}))

def vac_access_check(request):
    return get_object_or_404(User_info, user_id=request.user.id).vacs_access


def server_error(request):
    return render(request, "misc/500.html", status=500)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    return render(request, "misc/404.html",{"path": request.path},status=404)


def get_key_from_dict_by_value(dict, value):
    return [k for k, v in dict.items() if v == value][0]


def get_cross_vacations(vacations, users_colors, month_num_str):
    data = []
    # Определяем пересечения отпусков
    for i in range(len(vacations)):
        for j in range(i + 1, len(vacations)):
            if vacations[i] != vacations[j]:
                if (
                    (vacations[i].day_start >= vacations[j].day_start and vacations[i].day_end <= vacations[j].day_end)
                    or (vacations[i].day_start <= vacations[j].day_end and vacations[i].day_end > vacations[j].day_end)
                    or (vacations[i].day_start < vacations[j].day_start and vacations[i].day_end >= vacations[j].day_start)
                    or (vacations[i].day_start < vacations[j].day_start and vacations[i].day_end > vacations[j].day_end)
                ):
                    data.append(vacations[i])
                    data.append(vacations[j])
    
    vac_with_color = []
    for vac in set(data):
        user_id = vac.user.id 
        d = {
            'vac': vac,
            'range': f"{vac.day_start.day} {month_num_str[vac.day_start.month][:3]} - {vac.day_end.day} {month_num_str[vac.day_end.month][:3]}",
            'color': users_colors.get(user_id, "#default_color"),
        }
        vac_with_color.append(d)
    
    return vac_with_color


def copy_dict_for_js(month_all):
    month_all_for_js = {}
    for month, days in month_all.items():
        month_all_for_js[month] = {}
        for week, days_in_week in days.items():
            month_all_for_js[month][week] = {}
            for i in range(len(days_in_week)):
                month_all_for_js[month][week][i] = {}
                month_all_for_js[month][week][i]['name'] = month_all[month][week][i]['name']
                month_all_for_js[month][week][i]['date'] = {}
                for key in month_all[month][week][i]['data'].keys():
                    # Преобразование ключа в строку, если он не строка
                    key_str = str(key).replace(' ', '_')
                    month_all_for_js[month][week][i]['date'][key_str] = month_all[month][week][i]['data'][key]
                month_all_for_js[month][week][i]['data'] = month_all[month][week][i]['data']
    return month_all_for_js


def full_year(year):
    month_all = {
        1:'Январь', 2:'Февраль', 3:'Март',
        4:'Апрель', 5:'Май', 6:'Июнь',
        7:'Июль', 8:'Август', 9:'Сентябрь',
        10:'Октябрь', 11:'Ноябрь', 12:'Декабрь',
        }
    month_new = {}
    for i in range(1, 13):
        day = dt.datetime.today().replace(
            year=year,
            month=i,
            day=1
            )
        mnth_strt_d = day.replace(month=i, day=1).weekday()
        days_in_month = monthrange(year, i)[1]
        weeks, k = {}, 1
        weeks[k] = []
        #добавляем пустые клетки в начале месяца, если он начался не с понедельника
        [weeks[k].append('') for j in range(mnth_strt_d) if mnth_strt_d != 0]
        #заполняем месяц
        for j in range(1, days_in_month + 1):
            if mnth_strt_d < 7:
                weeks[k].append(j)
                mnth_strt_d += 1
            else:
                k += 1
                weeks[k] = []
                weeks[k].append(j)
                mnth_strt_d = 1
        #добавляем пустые клетки в конце месяца, если он закончился не в воскресенье    
        [weeks[k].append('') for j in range(mnth_strt_d, 7)]
        month_new[month_all[i]] = weeks
    return month_new


def vac_all(request, otd):
    if not vac_access_check(request):
        return render(request, 'no_rights.html',)

    today = dt.datetime.today().date()
    year = today.year

    current_user_name = request.user.get_full_name()

    # Если пользователь не является боссом
    if current_user_name not in bosses:
        otd_id = User_info.objects.filter(user_id=request.user.id)[0].otd_number_id
        unit = Unit.objects.filter(id=otd_id).first()
        if unit:
            otd = int(unit.description)
        else:
            otd = 0
        otd_users = User_info.objects.filter(otd_number_id=otd_id)
        otd_users_id = [user.user_id for user in otd_users]
        vacations = Vacation.objects.filter(user_id__in=otd_users_id, day_end__gte=today).order_by('day_start')
        otds_for_choise = [otd]
    else:
        # Если пользователь босс
        if otd == 0:  # Все отделы, которыми он руководит
            otds_for_choise = bosses[current_user_name]
            otd_ids = [Unit.objects.filter(description=descr).first().id for descr in otds_for_choise if Unit.objects.filter(description=descr).exists()]
            otd_users = User_info.objects.filter(otd_number_id__in=otd_ids)
        else:  # Выбран конкретный отдел
            unit = Unit.objects.filter(description=otd).first()
            if unit:
                otd_id = unit.id
                otd_users = User_info.objects.filter(otd_number_id=otd_id)
                otds_for_choise = [otd]
            else:
                otd_id = None
                otd_users = User_info.objects.none()
                otds_for_choise = []

        otd_users_id = [user.user_id for user in otd_users]
        vacations = Vacation.objects.filter(user_id__in=otd_users_id, day_end__gte=today).order_by('day_start')

    nearest_vacations = {}
    for vac in vacations:
        if vac.day_start >= today or (vac.day_start <= today <= vac.day_end):
            if vac.user.id not in nearest_vacations:
                nearest_vacations[vac.user.id] = vac
            elif vac.day_start < nearest_vacations[vac.user.id].day_start:
                nearest_vacations[vac.user.id] = vac

    filtered_vacations = list(nearest_vacations.values())

    vacation_start_dates = {}
    for vac in filtered_vacations:
        vacation_start_dates.setdefault(vac.user.get_full_name(), []).append(vac.day_start)

    users_colors = {}
    for vac in vacations:
        if vac.user.id not in users_colors.keys():  # Используем ID пользователя в качестве ключа
            users_colors[vac.user.id] = next(color_cycle)

    vacations_by_user = {}
    users_otd = User_info.objects.all()
    for vac in filtered_vacations:
        if vac.user.id not in vacations_by_user:
            user_info = users_otd.get(user_id=vac.user_id)
            position = user_info.position.position if user_info.position else "Не указана"
            vacations_by_user[vac.user.id] = {
                'name': vac.user.get_full_name(),
                'user_id': vac.user.id,
                'position': position,
                'otd': otd,
                'color': users_colors[vac.user.id],
                'sum': 0,
                'in_vacation': False,
                'dates': [],
                'vacation_periods': [],
                'vacation_start_dates': []
            }

            if vac.day_start <= today <= vac.day_end:
                vacations_by_user[vac.user.id]['in_vacation'] = True

            for u in users_otd:
                if u.user_id == vac.user_id:
                    vacations_by_user[vac.user.id]['otd'] = u.otd_number
                    break
        
        start_date = vac.day_start
        days_count = (vac.day_end - vac.day_start).days + 1
        
        # Подсчитываем количество праздничных дней в отпуске (включая выходные и будние)
        holidays_in_vacation = 0
        for y, m_d in holidays.items():
            for m, d in m_d.items():
                for day in d:
                    month_number = get_key_from_dict_by_value(month_num_str, m)
                    holiday_date = today.replace(year=int(y), month=month_number, day=day)

                    # Проверяем, попадает ли праздник в диапазон отпуска
                    if start_date <= holiday_date <= start_date + dt.timedelta(days=days_count - 1):
                        holidays_in_vacation += 1

        # Уменьшаем количество дней отпуска на праздничные дни
        actual_days_count = days_count - holidays_in_vacation

        # Устанавливаем дату окончания, добавляя количество праздничных дней
        end_date = start_date + dt.timedelta(days=actual_days_count + holidays_in_vacation - 1)

        # Обновляем данные пользователя с корректными значениями
        vacations_by_user[vac.user.id]['vacation_start_dates'].append((start_date, actual_days_count))

        vacations_by_user[vac.user.id]['dates'].append(
            {'d': f"{vac.day_start.day} {month_num_str[vac.day_start.month][:3]} - {vac.day_end.day} {month_num_str[vac.day_end.month][:3]}",
            'vac_id': vac.id,
            }
        )

        vacations_by_user[vac.user.id]['sum'] += actual_days_count
        formatted_start = f"{start_date.day} {months_ru[start_date.month]} {start_date.year}"
        formatted_end = f"{end_date.day} {months_ru[end_date.month]} {end_date.year}"
        vacations_by_user[vac.user.id]['vacation_periods'].append(f"{formatted_start} - {formatted_end}")

    return render(
        request,
        'vac_all.html',
        {'today': today,
         'year': year,
         'otd': otd,
         'len_vacations': len(filtered_vacations),
         'vacations_by_user': vacations_by_user,
         'holidays': holidays.get(year, {}),
         'otds_for_choise': otds_for_choise,
         'otd_users_full_names': [request.user],
         'vacation_start_dates': vacation_start_dates,
         'show_button': True,
         'navbar_style': 'custom-navbar',
         'users_colors': users_colors,
         'bosses': list(bosses.keys()),
        }
    )


def vac_calendars(request, otd, year=None):
    if not vac_access_check(request):
        return render(request, 'no_rights.html')

    current_year = dt.datetime.now().year
    next_year = current_year + 1
    current_user_name = request.user.get_full_name()
    today = dt.datetime.today().date()

    year = request.GET.get('year', current_year)
    year = int(year)

    years_in_vacations = set(Vacation.objects.values_list('year', flat=True))  # Исключаем дубликаты
    years_in_vacations.add(str(next_year))
    years_range = sorted([int(y) for y in years_in_vacations], reverse=True)

    # Проверка, является ли пользователь боссом
    if current_user_name not in bosses.keys():
        otd_id = User_info.objects.filter(user_id=request.user.id).first().otd_number_id
        otd_users = User_info.objects.filter(otd_number_id=otd_id)
        otd_users_id = [user.user_id for user in otd_users]
        unit = Unit.objects.filter(id=otd_id).first()
        if unit:
            linked_units = [unit.description]
        else:
            linked_units = ["Неизвестный отдел"]
    else:
        if otd == 0:
            linked_units = bosses[current_user_name]
            otd_ids = [Unit.objects.filter(description=desc).first().id for desc in linked_units]
        else:
            otd_id = Unit.objects.filter(description=otd).first().id
            linked_units = [otd]
            otd_ids = [otd_id]

        otd_users = User_info.objects.filter(otd_number_id__in=otd_ids)
        otd_users_id = [user.user_id for user in otd_users]

    otds_for_choise = linked_units

    otd_data = []
    units = Unit.objects.filter(description__in=linked_units)
    for unit in units:
        unit_users = User_info.objects.filter(otd_number_id=unit.id)
        unit_user_ids = [user.user_id for user in unit_users]
        vacations_count = Vacation.objects.filter(user_id__in=unit_user_ids, year=str(year)).count()

        if vacations_count > 0:
            otd_data.append({
                'otd': unit.title,
                'otd_description': unit.description,
                'employees': unit_users.count(),
                'vacations': vacations_count
            })

    filtered_years_vacations_count = {}
    for y in years_range:
        filtered_years_vacations_count[y] = Vacation.objects.filter(
            user_id__in=otd_users_id, year=str(y)
        ).count()

    has_vacations_in_linked_units = any(count > 0 for count in filtered_years_vacations_count.values())

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'otd_data': otd_data,
            'linked_units': linked_units,
        })

    return render(
        request,
        'vac_calendars.html',
        {   'today': today,
            'year': year,
            'current_year': current_year,
            'next_year': next_year,
            'otd': otd,
            'years_vacations_count': filtered_years_vacations_count,
            'otds_for_choise': otds_for_choise,
            'bosses': list(bosses.keys()),
            'current_user_name': current_user_name,
            'navbar_style': 'custom-navbar',
            'show_button': True,
            'years_range': years_range,
            'has_vacations_in_linked_units': has_vacations_in_linked_units,
        }
    )


def vac_2(request, year, otd):
    if not vac_access_check(request):
        return render(request, 'no_rights.html',)

    if year == 0:
        year = dt.datetime.today().year
    today = dt.datetime.today().date()
    month_all = full_year(year)

    bosses_list = list(bosses.keys())
    current_user_name = request.user.get_full_name()

    if request.user.get_full_name() not in bosses.keys():
        otd_id = User_info.objects.filter(user_id=request.user.id)[0].otd_number_id
        unit = Unit.objects.filter(id=otd_id).first()
        if unit:
            otd = int(unit.description)
        else:
            otd = 0
        otd_users = User_info.objects.filter(otd_number_id=otd_id) 
        otd_users_id = [user.user_id for user in otd_users] 
        vacations = Vacation.objects.filter(user_id__in=otd_users_id, year=str(year))
        otds_for_choise = [otd]
        otd_users_full_names = [request.user]
    else:
        if otd == 0:  # Все
            vacations = Vacation.objects.filter(year=str(year))
        else:
            otd_id = Unit.objects.filter(description=otd)[0].id  
            otd_users = User_info.objects.filter(otd_number_id=otd_id)  
            otd_users_id = [user.user_id for user in otd_users]  
            vacations = Vacation.objects.filter(user_id__in=otd_users_id, year=str(year))
        otds_for_choise = bosses[request.user.get_full_name()]


        otd_ids = [Unit.objects.filter(description=descr)[0].id for descr in bosses[request.user.get_full_name()]]

        otd_users = User_info.objects.filter(otd_number_id__in=otd_ids) 
        otd_users_id = [user.user_id for user in otd_users]
        otd_users_full_names = [user for user in User.objects.filter(id__in=otd_users_id)]


    vacation_start_dates = {}
    for vac in vacations:
        if vac.user_id not in vacation_start_dates:
            vacation_start_dates[vac.user_id] = []

        vacation_start_dates[vac.user_id].append(vac.day_start)

    users_colors = {}
    for vac in vacations:
        if vac.user_id not in users_colors:
            users_colors[vac.user_id] = next(color_cycle)

    cross_vacations = get_cross_vacations(vacations, users_colors, month_num_str)


    vacations_by_user = {}
    users_otd = User_info.objects.all()
    for vac in vacations:
        if vac.user_id not in vacations_by_user:
            vacations_by_user[vac.user_id] = {
                'color': users_colors[vac.user_id],
                'dates': [],
                'sum': 0,
                'otd': '',
                'user_id': vac.user_id,
                'vacation_start_dates': [],
                'vacation_end_dates': [],
                'user': vac.user
            }
            for u in users_otd:
                if u.user_id == vac.user_id:
                    vacations_by_user[vac.user_id]['otd'] = u.otd_number
                    break
        
        start_date = vac.day_start
        days_count = (vac.day_end - vac.day_start).days + 1  

        # Считаем количество праздничных дней, которые попадают в отпуск
        holidays_count = 0
        for y, m_d in holidays.items():
            for m, d in m_d.items():
                for day in d:
                    month_number = get_key_from_dict_by_value(month_num_str, m)
                    holiday_date = today.replace(year=int(y), month=month_number, day=day)

                    if vac.day_start <= holiday_date <= vac.day_end:
                        holidays_count += 1

        days_count -= holidays_count
        end_date = start_date + dt.timedelta(days=days_count - 1)
        end_date += dt.timedelta(days=holidays_count)

        vacations_by_user[vac.user_id]['vacation_start_dates'].append((start_date, days_count))
        vacations_by_user[vac.user_id]['dates'].append(
            {'d': f"{vac.day_start.day} {month_num_str[vac.day_start.month][:3]} - {vac.day_end.day} {month_num_str[vac.day_end.month][:3]}",
            'vac_id': vac.id}
        )
        vacations_by_user[vac.user_id]['sum'] += (vac.day_end - vac.day_start).days + 1
        vacations_by_user[vac.user_id]['vacation_end_dates'].append(end_date)
        
        for y, m_d in holidays.items():
            for m, d in m_d.items():
                for day in d:
                    month_number = get_key_from_dict_by_value(month_num_str, m)
                    date = today.replace(year=int(y), month=month_number, day=day)
                    if vac.day_start <= date <= vac.day_end:
                        vacations_by_user[vac.user_id]['sum'] -= 1

    for month, weeks in month_all.items():
        for week, days_in_week in weeks.items():
            for i in range(len(days_in_week)):
                data = {}
                date = ""
                if str(days_in_week[i]) != "":
                    month_number = get_key_from_dict_by_value(month_num_str, month)
                    day = today.replace(year=int(year), month=month_number, day=days_in_week[i])
                    for vac in vacations:
                        if day >= vac.day_start and day <= vac.day_end:
                            data[vac.user_id] = {
                                'date': f"{vac.day_start} - {vac.day_end}",
                                'color': users_colors[vac.user_id],
                                'vac_id': vac.id,
                            }
                    m = [k for k, v in month_num_str.items() if v == month][0]
                    date = today.replace(year=int(year), month=m, day=int(days_in_week[i]))
                month_all[month][week][i] = {'name': days_in_week[i], 'data': data, 'date': date}

    month_all_for_js = copy_dict_for_js(month_all)
    
    if year in holidays.keys():
        h_days = holidays[year]
    else:
        h_days = {}

    all_vac_for_js = {}
    for vac in vacations:
        all_vac_for_js[vac.id] = [str(vac.day_start), str(vac.day_end), vac.how_long]

    user_names = {user.id: user.get_full_name() for user in User.objects.filter(id__in=otd_users_id)}

    return render(
        request,
        'vac_new_calendar.html',
        {'today': today,
         'year': year,
         'otd': otd,
         **month_all,
         'json_data': json.dumps(month_all_for_js),
         'json_data_vacs': json.dumps(all_vac_for_js),
         'user_names': json.dumps(user_names),
         
         'cross_vacations': cross_vacations,
         'len_cross_vacations': len(cross_vacations),
         'len_vacations': vacations.count,
         'special_work_days': special_work_days,
         'vacations_by_user': vacations_by_user,
         'holidays': h_days,
         'otds_for_choise': otds_for_choise,
         'bosses': [key for key in bosses.keys()],
         'otd_users_full_names': otd_users_full_names,
         'vacation_start_dates': vacation_start_dates,

         'show_button': True,
         'show_add_leave_button': True,
         'bosses_list': json.dumps(bosses_list),
         'current_user_name': current_user_name,
         'navbar_style': 'custom-navbar',
         'show_vacation_link': True,
        }
    )
      

def vac_2_days(request, year, otd):
    if not vac_access_check(request):
        return render(request, 'no_rights.html',)

    if year == 0:
        year = dt.datetime.today().year

    today = dt.datetime.today().date()
    bosses_list = list(bosses.keys())
    current_user_name = request.user.get_full_name()

    user_names = {}
    vacation_start_dates = {}
    users_colors = {}
    vacations_by_user = {}

    # Определяем отделы для выбора и отпуска
    if current_user_name not in bosses.keys():
        otd_id = User_info.objects.filter(user_id=request.user.id).first().otd_number_id
        unit = Unit.objects.filter(id=otd_id).first()
        if unit:
            otd = int(unit.description)
        else:
            otd = 0
        otd_users = User_info.objects.filter(otd_number_id=otd_id)
        otd_users_id = [user.user_id for user in otd_users]
        vacations = Vacation.objects.filter(user_id__in=otd_users_id, year=str(year))
        otds_for_choise = [otd]
        otd_users_full_names = [request.user]
        user_names = {user.id: user.get_full_name() for user in User.objects.filter(id__in=otd_users_id)}
    else:
        if otd == 0:  # Все отделы
            vacations = Vacation.objects.filter(year=str(year))
        else:
            otd_id = Unit.objects.filter(description=otd).first().id
            otd_users = User_info.objects.filter(otd_number_id=otd_id)
            otd_users_id = [user.user_id for user in otd_users]
            vacations = Vacation.objects.filter(user_id__in=otd_users_id, year=str(year))
        otds_for_choise = bosses[current_user_name]
        otd_ids = [Unit.objects.filter(description=descr).first().id for descr in otds_for_choise]
        otd_users = User_info.objects.filter(otd_number_id__in=otd_ids)
        otd_users_id = [user.user_id for user in otd_users]
        otd_users_full_names = [user for user in User.objects.filter(id__in=otd_users_id)]
        user_names = {user.id: user.get_full_name() for user in User.objects.filter(id__in=otd_users_id)}

    # Обработка данных отпусков
    for vac in vacations:
        if vac.user_id not in vacation_start_dates:
            vacation_start_dates[vac.user_id] = []
        vacation_start_dates[vac.user_id].append(vac.day_start)

        if vac.user_id not in users_colors:
            users_colors[vac.user_id] = next(color_cycle)

        if vac.user_id not in vacations_by_user:
            vacations_by_user[vac.user_id] = {
                'color': users_colors[vac.user_id],
                'dates': [],
                'sum': 0,
                'otd': '',
                'user_id': vac.user_id,
                'vacation_start_dates': [],
                'vacation_end_dates': [],
                'employee_name': user_names.get(vac.user_id, "Неизвестный сотрудник"),
            }
            for u in User_info.objects.all():
                if u.user_id == vac.user_id:
                    vacations_by_user[vac.user_id]['otd'] = u.otd_number
                    break

        start_date = vac.day_start
        days_count = (vac.day_end - vac.day_start).days + 1

        holidays_count = sum(
            1
            for y, m_d in holidays.items()
            for m, d in m_d.items()
            for day in d
            if vac.day_start <= today.replace(year=int(y), month=get_key_from_dict_by_value(month_num_str, m), day=day) <= vac.day_end
        )

        days_count -= holidays_count
        end_date = start_date + dt.timedelta(days=days_count - 1) + dt.timedelta(days=holidays_count)

        vacations_by_user[vac.user_id]['vacation_start_dates'].append((start_date, days_count))
        vacations_by_user[vac.user_id]['dates'].append({
            'd': f"{vac.day_start.day} {month_num_str[vac.day_start.month][:3]} - {vac.day_end.day} {month_num_str[vac.day_end.month][:3]}",
            'vac_id': vac.id,
        })
        vacations_by_user[vac.user_id]['sum'] += (vac.day_end - vac.day_start).days + 1
        vacations_by_user[vac.user_id]['vacation_end_dates'].append(end_date)

    h_days = holidays.get(year, {})

    return render(
        request,
        'vac_schedule_days.html',
        {'today': today,
         'year': year,
         'otd': otd,
         'len_vacations': vacations.count(),
         'vacations_by_user': vacations_by_user,
         'holidays': h_days,
         'otds_for_choise': otds_for_choise,
         'bosses': [key for key in bosses.keys()],
         'otd_users_full_names': otd_users_full_names,
         'vacation_start_dates': vacation_start_dates,
         'show_button': True,
         'show_add_leave_button': True,
         'bosses_list': json.dumps(bosses_list),
         'current_user_name': current_user_name,
         'navbar_style': 'custom-navbar',
         'show_vacation_link': True,
        }
    )


@login_required
def vacation_new(request, year):
    if not vac_access_check(request):  # Проверяем доступ к отпуску
        return render(request, 'no_rights.html')

    # Инициализация формы и модели отпуска
    vacation = Vacation(user_id=request.user.id)
    form = VacationForm(request.POST or None, files=request.FILES or None, instance=vacation)

    # Определяем, является ли пользователь боссом
    current_user_name = request.user.get_full_name()
    is_boss = current_user_name in bosses

    employees = None

    employee_name = request.GET.get('employee_name', None)

    if is_boss:
        boss_departments = bosses[current_user_name]
        department_ids = Unit.objects.filter(description__in=boss_departments).values_list('id', flat=True)
        employees = User_info.objects.filter(otd_number_id__in=department_ids).select_related('user', 'position')

    selected_employee_name = current_user_name
    
    if form.is_valid():
        vac = form.save(commit=False)

        if is_boss and 'employee' in request.POST:
            selected_employee_id = request.POST['employee']
            vac.user_id = selected_employee_id
            selected_employee_name = User.objects.get(id=selected_employee_id).get_full_name()
        else:
            vac.user_id = request.user.id

        if vac.day_end:
            # Если дата окончания введена вручную, используем ее как есть
            vac.day_end += timedelta(days=1)
        elif vac.day_start and vac.how_long:
            # Если указана дата начала и длительность отпуска, рассчитываем дату окончания
            current_date = vac.day_start
            remaining_days = int(vac.how_long)

            while remaining_days > 0:
                current_date += timedelta(days=1)
                if current_date not in holidays:
                    remaining_days -= 1

            vac.day_end = current_date 
        elif vac.day_start and vac.day_end:
            # Если указаны обе даты, рассчитываем количество рабочих дней
            delta_days = (vac.day_end - vac.day_start).days
            working_days = 0
            current_date = vac.day_start

            while current_date < vac.day_end:
                if current_date not in holidays:
                    working_days += 1
                current_date += timedelta(days=1)

            vac.how_long = working_days

        if vac.day_start:
            vac.day_start += timedelta(days=1)

        vac.save()

        if employee_name:
            return redirect('vac_2', year=year, otd=0)
        elif 'employee' in request.POST and request.POST['employee'] != str(request.user.id):
            return redirect(f'{reverse("vac_all_vacations")}?user={selected_employee_name}')
        else:
            return redirect('vac_my_vacations')

    current_holidays = holidays.get(year, {})
    holidays_json = json.dumps(current_holidays)
    
    context = {
        'form': form,
        'user': request.user,
        'employees': employees,
        'is_boss': is_boss,
        'navbar_style': 'custom-navbar',
        'bosses': list(bosses.keys()),
        'year': year,
        'show_person': True,
        'holidays_json': holidays_json,
        'employee_name': employee_name,
    }

    return render(request, 'vacation_new.html', context)


@login_required
def vacation_edit(request, year, vac_id):
    if not vac_access_check(request):  
        return render(request, 'no_rights.html')

    vac = get_object_or_404(Vacation, id=vac_id)

    if vac.day_start and vac.day_end:
        delta_days = (vac.day_end - vac.day_start).days
        working_days = 0
        current_date = vac.day_start

        while current_date <= vac.day_end:
            if current_date not in holidays.get(year, []): 
                working_days += 1
            current_date += timedelta(days=1)

        vac.how_long = working_days

    vac.day_start = str(vac.day_start)[:-15]
    vac.day_end = str(vac.day_end)[:-15]

    form = VacationForm(request.POST or None, files=request.FILES or None, instance=vac)

    # Получаем имя и должность сотрудника, связанного с текущим отпуском
    employee_name = vac.user.get_full_name()
    employee_position = None
    if hasattr(vac.user, 'user_info'):
        user_info = vac.user.user_info.first() 
        if user_info and user_info.position:
            employee_position = user_info.position.position

    if form.is_valid():
        vac = form.save(commit=False)

        if vac.day_end:
            vac.day_end += timedelta(days=1)
        elif vac.day_start and vac.how_long:
            current_date = vac.day_start
            remaining_days = int(vac.how_long)

            while remaining_days > 0:
                current_date += timedelta(days=1)
                if current_date not in holidays.get(year, []): 
                    remaining_days -= 1

            vac.day_end = current_date
        elif vac.day_start and vac.day_end:
            delta_days = (vac.day_end - vac.day_start).days
            working_days = 0
            current_date = vac.day_start

            while current_date < vac.day_end:
                if current_date not in holidays.get(year, []):  
                    working_days += 1
                current_date += timedelta(days=1)

            vac.how_long = working_days

        if vac.day_start:
            vac.day_start += timedelta(days=1)

        if vac.day_start >= vac.day_end:
            return render(
                request,
                'vacation_edit.html',
                {
                    'form': form,
                    'vac_id': vac_id,
                }
            )

        vac.save()
        from_param = request.GET.get('from')

        if from_param == 'calendars':
            return redirect('vac_2', year=year, otd=0)
        elif from_param == 'all_vacations':
            return redirect(f'{reverse("vac_all_vacations")}?user={employee_name}')
        else:
            return redirect('vac_my_vacations')

    current_holidays = holidays.get(year, {})
    holidays_json = json.dumps(current_holidays)
    
    return render(
        request,
        'vacation_edit.html',
        {
            'form': form,
            'user': request.user,
            'edit': True,
            'vac_id': vac_id,
            'year': year,
            'value': vac,
            'employee_name': employee_name,
            'employee_position': employee_position, 
            'navbar_style': 'custom-navbar',
            'bosses': list(bosses.keys()),
            'redact_vac': True,
            'show_button': True,
            'holidays_json': holidays_json,
        }
    )


@login_required
def vacation_delete(request, vac_id):
    if not vac_access_check(request):
        return render(request, 'no_rights.html',)
    
    redirect_from = request.GET.get('from', None)

    vac = get_object_or_404(Vacation, id=vac_id)
    year = vac.day_start.year
    vac.delete()

    if redirect_from == 'calendars':
        return redirect('vac_2', year=year, otd=0)
    elif redirect_from == 'all_vacations':
        return redirect('vac_all_vacations') 
    else:
        return redirect('vac_my_vacations')


def vacation_detail(request, vac_id):
    if not vac_access_check(request):
        return render(request, 'no_rights.html')

    current_user_name = request.user.get_full_name()

    if current_user_name not in bosses:
        vacation = get_object_or_404(Vacation, id=vac_id, user_id=request.user.id)
    else:
        # Получаем список отделов, которые под управлением босса
        boss_departments = bosses[current_user_name]

        boss_departments = [str(department) for department in boss_departments]

        department_ids = Unit.objects.filter(description__in=boss_departments).values_list('id', flat=True)

        allowed_users = User_info.objects.filter(otd_number_id__in=department_ids).values_list('user_id', flat=True)

        if not allowed_users:
            raise Http404("No users found for this boss's departments.")

        vacation = get_object_or_404(Vacation, id=vac_id, user_id__in=allowed_users)

    vacation_user_name = vacation.user.get_full_name()

    # Дальнейшая обработка отпуска
    start_date = vacation.day_start
    end_date = vacation.day_end
    total_days = (end_date - start_date).days + 1

    holidays_in_vacation = sum(
        1
        for year, months in holidays.items()
        for month, days in months.items()
        for day in days
        if start_date <= dt.date(int(year), get_key_from_dict_by_value(month_num_str, month), day) <= end_date
    )

    actual_days_count = total_days - holidays_in_vacation
    adjusted_end_date = start_date + dt.timedelta(days=actual_days_count + holidays_in_vacation - 1)

    from_page = request.GET.get('from', None)
    year = vacation.day_start.year

    return render(
        request,
        'vacation_detail.html',
        {
            'start_date': start_date.strftime('%d.%m.%Y'),
            'end_date': adjusted_end_date.strftime('%d.%m.%Y'),
            'days_count': actual_days_count,
            'vacation_user_name': vacation_user_name,
            'show_button': True,
            'vacation': vacation,
            'navbar_style': 'custom-navbar',
            'bosses': list(bosses.keys()),
            'show_vacation_detail': True,
            'from_page': from_page,
            'year': year,
        }
    )


def vac_all_vacations(request):
    today = dt.datetime.today()
    current_year = today.year
    year_range = range(current_year - 1, current_year + 2)

    selected_otd = request.GET.get('otd', '') 
    selected_user = request.GET.get('user', '')
    selected_year = request.GET.get('year', '')

    current_user_name = request.user.get_full_name()
    filters = {}
    user_colors = {}

    if current_user_name in bosses:
        boss_departments = bosses[current_user_name]
        boss_departments = [str(department) for department in boss_departments]
        department_ids = Unit.objects.filter(description__in=boss_departments).values_list('id', flat=True)
        filters['user__user_info__otd_number_id__in'] = department_ids

    if selected_otd:
        otd = Unit.objects.filter(title=selected_otd).first()
        if otd:
            filters['user__user_info__otd_number_id'] = otd.id

    if selected_user:
        name_parts = selected_user.split()
        if len(name_parts) == 2:
            filters['user__first_name'] = name_parts[0]
            filters['user__last_name'] = name_parts[1]

    if selected_year:
        filters['year'] = selected_year

    vacations = Vacation.objects.filter(**filters)

    vacation_count = vacations.count()

    otds_for_choise = Unit.objects.all()
    if current_user_name in bosses:
        otds_for_choise = otds_for_choise.filter(description__in=bosses[current_user_name])
        department_ids = Unit.objects.filter(description__in=bosses[current_user_name]).values_list('id', flat=True)
        users_for_filter = User.objects.filter(user_info__otd_number_id__in=department_ids)
    else:
        users_for_filter = User.objects.all()

    years_vacations_count = {}
    for year in year_range:
        year_filters = filters.copy()
        
        if 'year' in year_filters:
            del year_filters['year']
        
        year_filters['year'] = str(year)

        years_vacations_count[year] = Vacation.objects.filter(**year_filters).count()

    # Список отпусков с подсчитанными днями и периодами
    vacations_list = []
    for vac in vacations:
        start_date = vac.day_start
        days_count = (vac.day_end - vac.day_start).days + 1

        holidays_in_vacation = sum(
            1
            for y, m_d in holidays.items()
            for m, d in m_d.items()
            for day in d
            if start_date <= today.replace(year=int(y), month=get_key_from_dict_by_value(month_num_str, m), day=day).date() <= start_date + dt.timedelta(days=days_count - 1)
        )

        actual_days_count = days_count - holidays_in_vacation
        end_date = start_date + dt.timedelta(days=actual_days_count + holidays_in_vacation - 1)

        user_info = vac.user.user_info.first()
        department = user_info.otd_number.title if user_info and user_info.otd_number else 'Не указан'

        user_name = vac.user.id
        if user_name not in user_colors:
            user_colors[user_name] = next(color_cycle)

        # Добавляем отпуск в список
        vacations_list.append({
            'user': vac.user.get_full_name(),
            'period': f"{start_date.day} {months_ru[start_date.month]} {start_date.year} - {end_date.day} {months_ru[end_date.month]} {end_date.year}",
            'days_count': actual_days_count,
            'id': vac.id,
            'is_current': start_date <= today.date() <= vac.day_end.date(),
            'department': department,
            'color': user_colors[user_name],
        })

    return render(
        request,
        'vac_all_vacations.html',
        {   'today': today,
            'year': selected_year,
            'otds_for_choise': otds_for_choise,
            'users_for_filter': users_for_filter,
            'vacations': vacations_list,
            'selected_otd': selected_otd,
            'selected_user': selected_user,
            'selected_year': selected_year,
            'year_range': year_range,
            'years_vacations_count': years_vacations_count,
            'show_button': True,
            'navbar_style': 'custom-navbar',
            'bosses': list(bosses.keys()),
            'show_all_vacations': True,
            'vacation_count': vacation_count,
        }
    )


def vac_my_vacations(request):
    if not vac_access_check(request):
        return render(request, 'no_rights.html')

    today = dt.datetime.today().date()
    year = today.year

    # Получаем все отпуска текущего пользователя, начиная с текущей даты
    vacations = Vacation.objects.filter(
        user_id=request.user.id,
        day_end__gte=today
    ).order_by('day_start')

    vacations_list = []

    for vac in vacations:
        start_date = vac.day_start
        days_count = (vac.day_end - vac.day_start).days + 1

        holidays_in_vacation = sum(
            1
            for y, m_d in holidays.items()
            for m, d in m_d.items()
            for day in d
            if start_date <= today.replace(year=int(y), month=get_key_from_dict_by_value(month_num_str, m), day=day) <= start_date + dt.timedelta(days=days_count - 1)
        )

        actual_days_count = days_count - holidays_in_vacation
        end_date = start_date + dt.timedelta(days=actual_days_count + holidays_in_vacation - 1)

        # Добавляем отпуск в список
        vacations_list.append({
            'period': f"{start_date.day} {months_ru[start_date.month]} {start_date.year} - {end_date.day} {months_ru[end_date.month]} {end_date.year}",
            'days_count': actual_days_count,
            'id': vac.id,
            'is_current': start_date <= today <= vac.day_end.date(),
        })
    
    vacation_year = None
    
    for vacation in vacations_list:
        start_date = vacation['period'].split(' ')[-1]
        vacation_year = int(start_date)
        vacation['vacation_year'] = vacation_year

    return render(
        request,
        'vac_my_vacations.html',
        {
            'today': today,
            'year': year,
            'vacation_year': vacation_year,
            'vacations_list': vacations_list,
            'show_button': True,
            'navbar_style': 'custom-navbar',
            'bosses': list(bosses.keys()),
            'show_my_vacations': True,
        }
    )
        

def import_vacations(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            msg.error(request, "Файл не выбран.")
            return redirect(reverse('import_vacations'))

        if not file.name.endswith(('.xlsx', '.xls')):
            msg.error(request, "Неверный формат файла. Загрузите файл в формате .xlsx или .xls.")
            return redirect(reverse('import_vacations'))
        
        try:
            df = pd.read_excel(file)

            required_columns = ['Сотрудник', 'Отдел', 'Дата начала', 'Дата окончания']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                msg.error(request, f"В файле отсутствуют обязательные колонки: {', '.join(missing_columns)}.")
                return redirect(reverse('import_vacations'))

            df['Дата начала'] = pd.to_datetime(df['Дата начала'], format='%d.%m.%Y', dayfirst=True)
            df['Дата окончания'] = pd.to_datetime(df['Дата окончания'], format='%d.%m.%Y', dayfirst=True)

            if df['Дата начала'].isnull().any() or df['Дата окончания'].isnull().any():
                msg.error(request, "Некорректный формат дат в файле.")
                return redirect(reverse('import_vacations'))
            
            new_vacations = 0
            first_year = None 
            errors_found = False
            
            for index, row in df.iterrows():
                try:
                    full_name = row['Сотрудник'].strip()
                    first_name, last_name = full_name.split(' ', 1)

                    unit = Unit.objects.filter(description=row['Отдел']).first()
                    if not unit:
                        msg.error(
                            request,
                            f"Ошибка на строке {index + 1}: отдел '{row['Отдел']}' не найден."
                        )
                        errors_found = True
                        continue

                    user_info = User_info.objects.filter(
                        user__first_name=first_name,
                        user__last_name=last_name,
                        otd_number=unit
                    ).first()
                    if not user_info:
                        msg.error(
                            request,
                            f"Ошибка на строке {index + 1}: сотрудник '{full_name}' не принадлежит отделу '{row['Отдел']}'."
                        )
                        errors_found = True
                        continue

                    user = user_info.user

                    start_date = pd.to_datetime(row['Дата начала'], dayfirst=True) + timedelta(days=1)
                    end_date = pd.to_datetime(row['Дата окончания'], dayfirst=True) + timedelta(days=1)

                    if start_date > end_date:
                        msg.error(
                            request, 
                            f"Ошибка на строке {index + 1}: дата начала ({start_date.strftime('%d.%m.%Y')}) больше даты окончания ({end_date.strftime('%d.%m.%Y')})."
                        )
                        errors_found = True
                        continue
                    
                    if first_year is None:
                        first_year = start_date.year

                    existing_vacation = Vacation.objects.filter(
                        user=user,
                        day_start=start_date,
                        day_end=end_date,
                        user__user_info__otd_number=unit
                    ).exists()

                    if existing_vacation:
                        continue
                    
                    Vacation.objects.create(
                        user=user,
                        day_start=start_date,
                        day_end=end_date
                    )
                    new_vacations += 1
                except Exception:
                    errors_found = True
                    continue
            
            if not errors_found:
                msg.success(request, f"Добавлено новых отпусков: {new_vacations}.")
                return redirect(reverse('vac_2', kwargs={'otd': 0, 'year': first_year}))
            
        except Exception:
            msg.error(request, f"Ни одного отпуска не добавлено. Убедитесь, что все сотрудники уже добавлены.")
            return redirect(reverse('import_vacations'))

    context = {
        'navbar_style': 'custom-navbar',
        'import_vac': True,
        'show_button': True,
        'bosses': list(bosses.keys()),
    }

    return render(request, 'import_vacations.html', context)


def vac_my_profile(request):
    if not vac_access_check(request):
        return render(request, 'no_rights.html')

    today = dt.datetime.today().date()
    year = today.year
    user_info = User_info.objects.get(user=request.user)

    vacations = Vacation.objects.filter(
        user_id=request.user.id,
        day_end__gte=today
    ).order_by('day_start')

    vacations_list = []

    for vac in vacations:
        start_date = vac.day_start
        days_count = (vac.day_end - vac.day_start).days + 1

        holidays_in_vacation = sum(
            1
            for y, m_d in holidays.items()
            for m, d in m_d.items()
            for day in d
            if start_date <= today.replace(year=int(y), month=get_key_from_dict_by_value(month_num_str, m), day=day) <= start_date + dt.timedelta(days=days_count - 1)
        )

        actual_days_count = days_count - holidays_in_vacation
        end_date = start_date + dt.timedelta(days=actual_days_count + holidays_in_vacation - 1)

        vacations_list.append({
            'period': f"{start_date.day} {months_ru[start_date.month]} {start_date.year} - {end_date.day} {months_ru[end_date.month]} {end_date.year}",
            'days_count': actual_days_count,
            'id': vac.id,
            'is_current': start_date <= today <= vac.day_end.date(),
        })
    
    vacation_year = None
    
    for vacation in vacations_list:
        start_date = vacation['period'].split(' ')[-1]
        vacation_year = int(start_date)
        vacation['vacation_year'] = vacation_year

    return render(
        request,
        'my_profile.html',
        {
            'today': today,
            'year': year,
            'vacation_year': vacation_year,
            'vacations_list': vacations_list,
            'navbar_style': 'custom-navbar',
            'bosses': list(bosses.keys()),
            'my_profile': True,
            'user_info': user_info
        }
    )


@login_required
def profile_edit(request):
    user_info = User_info.objects.get(user=request.user)
    departments = Unit.objects.all()

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        name_parts = full_name.split(maxsplit=1)

        new_first_name = name_parts[0] if name_parts else ""
        new_last_name = name_parts[1] if len(name_parts) > 1 else ""
        new_email = request.POST.get("email", "").strip()

        updated = False

        if request.user.first_name != new_first_name:
            request.user.first_name = new_first_name
            updated = True
        if request.user.last_name != new_last_name:
            request.user.last_name = new_last_name
            updated = True
        if request.user.email != new_email:
            request.user.email = new_email
            updated = True

        if updated:
            request.user.save()

        position_name = request.POST.get("position", "").strip()
        if position_name and (not user_info.position or user_info.position.position != position_name):
            position, created = Position.objects.get_or_create(position=position_name)
            user_info.position = position
            updated = True

        new_department = Unit.objects.get(id=request.POST.get("department")) if request.POST.get("department") else None
        if user_info.otd_number != new_department:
            user_info.otd_number = new_department
            updated = True

        if updated:
            user_info.save()
            msg.success(request, "Сотрудник успешно обновлен.")

        return redirect('vac_my_profile')

    return render(request, 'profile_edit.html', {
        'user_info': user_info,
        'departments': departments,
        'navbar_style': 'custom-navbar',
        'bosses': list(bosses.keys()),
        'profile_edit': True,
        'show_button': True,
    })


@login_required
def delete_account(request):
    user = request.user

    User_info.objects.filter(user=user).delete()

    user.delete()

    logout(request)

    msg.success(request, "Ваш аккаунт был успешно удален.")
    return redirect('login')


def employees(request):
    return render(request, 'employees.html', {
        'navbar_style': 'custom-navbar',
        'bosses': list(bosses.keys()),
        'employees': True,
        'show_button': True,
    })