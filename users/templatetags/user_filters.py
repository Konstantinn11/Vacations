from django import template
from dateutil.relativedelta import *
import datetime as dt
import re
import os
from ..models import Unit
# В template.Library зарегистрированы все теги и фильтры шаблонов
# добавляем к ним и наш фильтр
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})

# синтаксис @register... , под который описана функция addclass() -
# это применение "декораторов", функций, обрабатывающих функции
# мы скоро про них расскажем. Не бойтесь соб@к
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter()
def to_str(value):
    return str(value)

#
@register.filter()
def get_diff(start: int, stop: int):
    return stop - start

@register.filter()
def cur_day(day):
    day = dt.datetime.now().date()
    return day

@register.filter()
def day_day(day):
    date_format = '%Y-%m-%d'
    new_day = dt.datetime.strptime(day, date_format)
    return new_day.date()


register.filter()
def day_day(day):
    date_format = '%Y-%m-%d'
    next_day = dt.datetime.strptime(day, date_format)  
    return next_day.date()

@register.filter()
def next_day(day):
    date_format = '%Y-%m-%d'
    next_day = dt.datetime.strptime(day, date_format)
    next_day += dt.timedelta(days=1)
    
    return next_day.date()

@register.filter()
def before_day(day):
    date_format = '%Y-%m-%d'
    before_day = dt.datetime.strptime(day, date_format)
    before_day -= dt.timedelta(days=1)
    return before_day.date()


@register.filter()
def cur_week(wk):
    wk = dt.datetime.strptime(str(dt.datetime.now().date()), '%Y-%m-%d').isocalendar()[1]
    year = dt.datetime.now().date().year
    wk = str(year) + '-' + str(wk)
    return wk


@register.filter()
def next_week(wk):
    year = int(wk[0:4])
    wk = int(wk[5:])
    #year = dt.datetime.now().date().year
    last_week = dt.date(year, 12, 31)
    if wk == last_week.isocalendar()[1]:
        year += 1
        return str(year) + '-' + str(1)
    wk += 1
    return str(year) + '-' + str(wk)

@register.filter()
def before_week(wk):
    year = int(wk[0:4])
    wk = int(wk[5:])
    #year = dt.datetime.now().date().year
    if wk == 1:
        year -= 1
        last_week = dt.date(year, 12, 31)
        return str(year) + '-' + str(last_week.isocalendar()[1])
    wk -= 1
    return str(year) + '-' + str(wk)


@register.filter()    
def cur_month(month):
    month = dt.datetime.now().date().month#
    year = dt.datetime.now().date().year#
    return str(year) + "-" + str(month)


@register.filter()    
def cur_month_new(m):  # m = [m, y]
    today = dt.datetime.today().date()
    month_all = {1:'Январь',
                 2:'Февраль',
                 3:'Март',
                 4:'Апрель',
                 5:'Май',
                 6:'Июнь',
                 7:'Июль',
                 8:'Август',
                 9:'Сентябрь',
                 10:'Октябрь',
                 11:'Ноябрь',
                 12:'Декабрь',}
    for key, val in month_all.items():
        if m[0] == val:
            return str(m[1]) + "-" + str(key)


    
    month = dt.datetime.now().date().month#
    year = dt.datetime.now().date().year#
    return str(year) + "-" + str(month)


@register.filter()    
def next_month(month):
    year = int(month[0:4])
    month = int(month[5:])
    if month == 12:
        year += 1
        month = 1
        return str(year) + "-" + str(month)
    month += 1
    return str(year) + "-" + str(month)


@register.filter()
def before_month(month):
    year = int(month[0:4])
    month = int(month[5:])
    if month == 1:
        year -= 1
        month = 12
        return str(year) + "-" + str(month)
    month -= 1
    return str(year) + "-" + str(month)

@register.filter()
def get_numb(numb):
    return "col-md-" + str(numb)

@register.filter()
def day_to_date(day):
    return day.date()

@register.filter()
def day_of_week(key):
    return key[12:]

@register.filter()
def day_of_week_p(key):
    if key[12:] == "Понедельник":
        return key[:12]+"Пн."
    if key[12:] == "Вторник":
        return key[:12]+"Вт."
    if key[12:] == "Среда":
        return key[:12]+"Ср."
    if key[12:] == "Четверг":
        return key[:12]+"Чт."
    if key[12:] == "Пятница":
        return key[:12]+"Пт."
    if key[12:] == "Суббота":
        return key[:12]+"Сб."
    if key[12:] == "Воскресенье":
        return key[:12]+"Вс."
    return key


@register.filter()
def day_from_week(k):
    return k[:10]


@register.filter()
def day_to_day(key, day):  # day не используется
    return key[:10] == str(dt.datetime.now().date())

@register.filter()
def day_to_month(key, month):
    if len(str(month)[5:]) == 1:
        return str(key)[5:7] == '0' + str(month)[5:]
    return str(key)[5:7] == str(month)[5:]

@register.filter()
def lange(start, stop):
    return stop - start

@register.filter
def file_name(link):
    slesh = link.rfind('/')
    return str(link)[slesh + 1:]


@register.filter
def start_to_range(start_id: int):
    values = []
    for i in range(1, start_id):
        values.append(i)       
    return values


@register.filter
def stop_to_range(stop_id: int):
    values = []
    for i in range(stop_id, 49):
        values.append(i)        
    return values

@register.filter
def new_chet(value: int):
    colors = {}
    i = 1
    while i < 49:
        colors[i] = "#E6E6E6"
        colors[i + 1] = "#E6E6E6"
        i += 4
    i = 3
    while i < 49:
        colors[i] = "#CCCCCC"
        colors[i + 1] = "#CCCCCC"
        i += 4
    if value in colors.keys():
        return colors[value]
    return


@register.filter
def chet(value: int):
    if value/2 == value//2:
        return 1
    return 2

@register.filter
def time_now(value: int):
    return (value - 1)//2 == int(str(dt.datetime.now().time())[:2])

@register.filter
def time_now_stop(value: int):
    return (value - 1)//2 == int(str(dt.datetime.now().time())[:2])

@register.filter
def time_now_for_head(value: int):
    return value == int(str(dt.datetime.now().time())[:2])

@register.filter
def get_num_rele(post):
    if post.text[:3] == "FIB" and post.text[4:6] != "BM":
        fibs = post.text.split('(')[1][:-1]
        result = []
        if fibs != '':
            for fib in fibs.split(','):
                if fib != 'MDU':
                    result.append(int(fib))
            print(result)
            return result
    return

@register.filter
def minus_one(p):
    return p - 1

@register.filter
def show_rele(post):
    if post.text[:3] == "FIB" and post.text[4:6] != "BM" and post.task_state_id == 2:
        if post.day.date() == dt.datetime.now().date():
            return (((post.t_start_id - 1)//2 <= int(str(dt.datetime.now().time())[:2])) and
                    ((post.t_stop_id - 1)//2 >= int(str(dt.datetime.now().time())[:2])))
    return

@register.filter
def time_to_range_new(value: int):
    colors = {}
    i = 0
    while i < 24:
        colors[i] = "#E6E6E6"
        i += 2
    i = 1
    while i < 24:
        colors[i] = "#CCCCCC"
        i += 2
    if value in colors.keys():
        return colors[value]
    return


@register.filter
def time_to_range(time: int):
    values = []
    for i in range(time):
        values.append(i)       
    return values

#FIB
@register.filter
def check_for_fib(text:str):    
    return text[:4]


@register.filter
def get_fib_nambers(text:str):    
    fib_in = []
    data = text.split('(')[1][:-1]
    fib_in = data.split(',')
    return fib_in

@register.filter
def get_fib_not_in_nambers(text:str):
    fib_in = []
    fib_not_in = []
    data = text.split('(')[1][:-1]
    fib_in = data.split(',')
    for i in range(1, 6):
        if str(i) not in fib_in:
            fib_not_in.append(i)
    if 'MDU' not in fib_in and 'MDU' not in fib_not_in:
            fib_not_in.append('MDU')
    return fib_not_in


@register.filter
def url_to_stand_id(text:str):
    #/day/2022-07-25/
    #/week/2022-30/
    #/stend/5/
    #/stend_with_over/5/
    
    if len(re.findall(r'[s][t][e][n][d][_][f][i][l][t][r][_][w][i][t][h][_][o][v][e][r]', text)) > 0:
        #print('stend_filtr_with_over')
        return text[23:24]
    if len(re.findall(r'[s][t][e][n][d][_][w][i][t][h][_][o][v][e][r]', text)) > 0:
        #print('stend_with_over')
        return text[17:18]
    if len(re.findall(r'[s][t][e][n][d][_][f][i][l][t][r]', text)) > 0:
        #print('stend_filtr_with_over')
        return text[13:14]
    if len(re.findall(r'[s][t][e][n][d]', text)) > 0:
        #print('stend')
        return text[7:8]
    if len(re.findall(r'[d][a][y]', text)) > 0 or len(re.findall(r'[w][e][e][k]', text)) > 0:
        return 100


@register.filter#дописать для mdu 238 итд
def url_to_filtr(text:str):
    #/stend/5/238/
    #print(text)
    if len(re.findall(r'[s][t][e][n][d][_][f][i][l][t][r][_][w][i][t][h][_][o][v][e][r]', text)) > 0:
        #print(text[25:-1])
        return text[25:-1]
    if len(re.findall(r'[s][t][e][n][d][/].[/]', text)) > 0:
        #print(text[9:-1])
        return text[9:-1]


@register.filter
def registration(field):
    field.field.required = True
    #return field


@register.filter
def today(m, d):  # m = [m, y]
    today = dt.datetime.today().date()
    month_all = {1:'Январь',
                 2:'Февраль',
                 3:'Март',
                 4:'Апрель',
                 5:'Май',
                 6:'Июнь',
                 7:'Июль',
                 8:'Август',
                 9:'Сентябрь',
                 10:'Октябрь',
                 11:'Ноябрь',
                 12:'Декабрь',}
    for key, val in month_all.items():
        if m[0] == val:
            today = today.replace(year=m[1], month=key, day=d)
            return today



@register.filter
def year_month(m, y):
    return [m, y]
    
@register.filter
def today_check(m, d):  # m = [m, y]
    today = dt.datetime.today().date()
    month_all = {1:'Январь',
                 2:'Февраль',
                 3:'Март',
                 4:'Апрель',
                 5:'Май',
                 6:'Июнь',
                 7:'Июль',
                 8:'Август',
                 9:'Сентябрь',
                 10:'Октябрь',
                 11:'Ноябрь',
                 12:'Декабрь',}

    for key, val in month_all.items():
        if m[0] == val:
            check = today.replace(year=m[1], month=key, day=d)
            break
    if today == check:
        return "="
    return today > check


@register.filter
def get_unit(unit):    
    try:         
        return str(unit).split('(')[1][:-1]
    except:
        return unit


@register.filter
def year_plus(year):    
    return year + 1

@register.filter
def year_minus(year):    
    return year - 1

@register.filter
def double_plus_one(value):    
    return value*2 + 1

@register.filter
def dict_len(dictionary):    
    return len(dictionary)


@register.filter
def index_of(mass, el):
    return mass.index(el)

@register.filter
def replace(text):
    if text is not None:
        if len(text) > 30:
            return text[:30] + '...'
    return text


@register.filter
def get_otd_number_from_full_name(text:str):
    if str(text).rfind('(') != -1:
        return str(text).split('(')[1][:-1]
    return str(text)


@register.filter()
def pro_week_before(day):
    if day !="":
        day = day - dt.timedelta(days=7)
        return day
    day = dt.datetime.now().date() - dt.timedelta(days=7)
    return day


@register.filter()
def pro_week_now(day):
    day = dt.datetime.now().date()
    return day


@register.filter()
def pro_week_future(day):
    if day !="":
        day = day + dt.timedelta(days=7)
        return day
    day = dt.datetime.now().date() + dt.timedelta(days=7)
    return day

@register.filter()
def len_of_mas(mas):
    print(len(mas))
    return len(mas)

@register.filter()
def get_el_of_array(a, n):  # array, number
    return a[n]


@register.filter()
def day_in_range(day, check_day):
    
    check_day = dt.datetime.strptime(str(check_day.date()), '%Y-%m-%d').date()
    day = dt.datetime.strptime(str(day), '%Y-%m-%d').date()
    dif = dt.datetime.now().date().isoweekday()    
    start_day = day - dt.timedelta(days= dif - 1)
    end_day = day + dt.timedelta(days= 7 - dif)
    return start_day <= check_day and end_day >= check_day
    
@register.filter()
def day_more_range(day, check_day):
    check_day = dt.datetime.strptime(str(check_day.date()), '%Y-%m-%d').date()
    day = dt.datetime.strptime(str(day), '%Y-%m-%d').date()
    dif = dt.datetime.now().date().isoweekday()    
    end_day = day + dt.timedelta(days= 7 - dif)
    return end_day >= check_day



#def today_check(m, d):  # m = [m, y]
@register.filter()
def day_vacation(m_y, day):

    month_all = {
        '01':'Январь', '02':'Февраль', '03':'Март',
        '04':'Апрель', '05':'Май', '06':'Июнь',
        '07':'Июль', '08':'Август', '09':'Сентябрь',
        '10':'Октябрь', '11':'Ноябрь', '12':'Декабрь',
        }
    month = ''
    if day != '':
        for key, value in month_all.items():
            if str(m_y[0]) == value:
                month = key

                date = str(m_y[1]) + '-' + month + '-' + str(day)
        
        check_day = dt.datetime.strptime(date, '%Y-%m-%d').date()
        return str(check_day)


@register.filter()
def month_trim(month):
    return month[0:3]

@register.filter()
def unit_id_from_number(number):
    return Unit.objects.filter(number=int(number))[0].id

@register.filter()
def count(arr):
    return len(arr)

#-----------------------------------------------
@register.filter()
def bet(param1, param2):
    return f'{param1.split(" ")[0]} ({str(round(int(param1.split(" ")[0])/int(param2.split(" ")[0])*100, 1)) + "%"})'

@register.filter()
def bet_res(param1, param2):
    p1 = float(param1.split("(")[1][:-2])
    p2 = float(param2.split("(")[1][:-2])
    p3 = (p1 + p2)/2
    return f'{str(round(p3, 1)) + "%"}'


@register.filter()
def bet_res_multiply(param1, param2):
    p1 = float(param1.split("(")[1][:-2])
    p2 = float(param2.split("(")[1][:-2])
    p3 = p1 * p2/100
    return f'{str(round(p3, 1)) + "%"}'

@register.filter()
def bet_more_res(param1, param2):
    p1 = float(param1.split("%")[0])
    p2 = float(param2.split("%")[0])
    p3 = (p1 + p2)/2
    return f'{str(round(p3, 1)) + "%"}'


@register.filter
def url_to_state_id(text: str):
    #  /nikolay.emelyanov/state/1/
    if text[-8:-3] == 'state':
        return text[-2:-1]

@register.filter
def replace_(word):
    return str(word).replace('_', ' ')

@register.filter
def vac(day, data):
    check_day = dt.datetime.strptime(day, '%Y-%m-%d').date()
    day_start = dt.datetime.strptime(data[0], '%Y-%m-%d').date()
    day_end = dt.datetime.strptime(data[1], '%Y-%m-%d').date()
    if check_day >= day_start and check_day <= day_end:
        return True

@register.filter
def color(key, data):
    return data[key]


@register.filter
def day_from_date(date):
    return date.day


@register.filter
def color_for_user(key, data):
    return data[key]


@register.filter
def url_to_btn(text:str):
    #http://127.0.0.1:8000/auth/vacations/all/306/
    try:
        number = int(text[-4:-1])
    except:
        number = 0
    print(number)
    return number


@register.filter
def url_to_year(text:str):
    #http://127.0.0.1:8000/auth/vacations/all/2023/306/
    try:
        year = int(text[-9:-5])
    except:
        year = 0
    print(year)
    return year

@register.filter
def file_exists(text:str):
    print(text)
    if text is not None:
        return os.path.isfile(text)   
    return False


@register.filter
def file_time(text:str):
    try:
        if os.path.isfile(text):
            return dt.datetime.fromtimestamp(os.path.getmtime(text)).date()
    except:
        return False

@register.filter
def color_for_date(date):
    return date.weekday()


@register.filter
def str_to_arr(string):
    arr = []
    for el in string.split("_"):
        arr.append(int(el))
    return arr

@register.filter
def today_or_not(day_start):
    today = dt.datetime.now().date()
    if day_start.date() < today:
        return True
    return False

@register.filter
def date_minus_date(d1, d2):
    return d1 - d2

@register.filter
def get_value_from_dict(d, k):
    return d.get(k)

@register.filter
def good_date(d):
    d -= dt.timedelta(days=1)
    return d

@register.filter
def get_phone_number(d, k):
    for item in d:
        if item.user_id == k:
            return  item.phone_number
    return '-'

@register.filter
def substring(s):
    if len(s) > 20:
        return s[:18] + '...'
    return s

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)