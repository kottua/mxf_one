import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import math

from src.max_bcg import scvhso_f
from src.max_dp import MEUA_f
from src.data_utils import calculate_plan_all, recalculate_plan_pcvsogap

# для ошибок
class Error(Exception):
    #класс для ошибок
    pass
class DataError(Error):
    #для ошибок в данніх
    #message -- суть ошибкі
    def __init__(self, message):
        self.message = message
# ДЛЯ РАСЧЕТА УРОВНЯ РАСПРОДАНОСТИ ОТ ДАТЫ и всяких календарных штучек

# функция для проверки того, является ли год високосным
def leap_year(n): 
    return n % 4 == 0 and (n % 100 != 0 or n % 400 == 0)
    
# функция для подсчета количества дней в месяце
def days_in_month(month, year): 
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    elif month == 2:
        if leap_year(year):
            return 29
        return 28
    return 30

# функция конвертирующая строку вида "dd/mm/yyyy" в обьект datetime.date
def from_string_to_date(s):
    [day, month, year] = map(int, s.split('/'))
    return date(year, month, day)

# функция которая возвращает разницу в днях между двумя датами подаными в виде строк формата "dd/mm/yyyy"
def days_between_two_strings(start, end):
    return (from_string_to_date(end) - from_string_to_date(start)).days

# суть этой функции в том чтобы для конкретной даты в формате "dd/mm/yyyy" вернуть соотвествующее значение pcvsop (распроданости) 
# используя вспомогательные функции заданые выше
def get_pcvsop_by_date(plan_df, selected_date_string):
    # ожидается что в таблице plan_df уже есть значения pcvsop, если это не так ничо не сработает:
    if not 'pcvsop' in list(plan_df.columns):
        raise DataError('no pcvsop data found!')
    # первым делом переведем дату из строки в формат datetime если на вход пришла строка
    if not isinstance(selected_date_string, date):
        selected_date = from_string_to_date(selected_date_string)
    else:
        selected_date = selected_date_string
    year, month = selected_date.year, selected_date.month
    next_date = date(year, month, days_in_month(month, year))
    # для начала обработка случаев "вылетания" даты за план
    # если введенная дата раньше даты начала плана то распроданость должна быть равна 0
    if selected_date <= date(plan_df['year'].values[0],plan_df['month'].values[0],1):
        return 0
    # если же наоборот, введеная дата позже даты конца плана - распроданость должна быть равна 1
    elif selected_date >= date(plan_df['year'].values[-1],plan_df['month'].values[-1],days_in_month(plan_df['month'].values[-1], plan_df['year'].values[-1])):
        return 1
    # в противном случае считаем что pcvsop ведет себя линейно ***
    else:
        # для даты dd/mm/yyy нам нужны две строчки из таблицы: строка за посл.день прошлого месяца и строка за посл день текущего
        pcvsop_1 = float(plan_df.loc[plan_df['year']==year].loc[plan_df['month']==month]['pcvsop']) # строка за посл день текущего месяца
        if month == 1: # если текущий месяц январь
            if not plan_df.loc[plan_df['year']==year-1].loc[plan_df['month']==12]['pcvsop'].empty:
                pcvsop_0 = float(plan_df.loc[plan_df['year']==year-1].loc[plan_df['month']==12]['pcvsop']) # строка за 31/12/yyyy-1 - посл месяц прошлого года в случае если текущий месяц январь
            else:
                pcvsop_0 = 0
            prev_date = date(year-1,12,31)
        else:
            #print(plan_df.loc[plan_df['year']==year].loc[plan_df['month']==month-1]['pcvsop'])
            if not plan_df.loc[plan_df['year']==year].loc[plan_df['month']==month-1]['pcvsop'].empty:
                pcvsop_0 = float(plan_df.loc[plan_df['year']==year].loc[plan_df['month']==month-1]['pcvsop']) # если месяц не январь - то берем распроданость по состоянию на посл день прошлого месяца 
            else:
                pcvsop_0 = 0
            prev_date = date(year,month-1,days_in_month(month-1, year))
        
        days_delta = (selected_date - prev_date).days    
        pcvsop_delta = ((pcvsop_1-pcvsop_0)/(next_date-prev_date).days) * days_delta
        return pcvsop_0 + pcvsop_delta
    
# функция которая возвращает продолжительность календарного плана в днях
def get_plan_lenght_in_days(plan_df):
    return (date(plan_df['year'].values[-1],plan_df['month'].values[-1],
                 days_in_month(plan_df['month'].values[-1], plan_df['year'].values[-1])) - 
            date(plan_df['year'].values[0],plan_df['month'].values[0],1)).days

# функция которая возвращает минимальное и максимальное время между двумя продажами
def get_min_max_timedelta(plan_df, stock_df):
    average_delta = get_plan_lenght_in_days(plan_df)/len(stock_df)
    return math.floor(average_delta/2), math.ceil(average_delta*1.5)

# функция которая накидывает pvca по дням - для текущего месяца плана
def modify_pvca_current_month(plan_df, current_date):
    days_in_current_month = days_in_month(current_date.month, current_date.year)
    average_daily_pvca = plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']==current_date.month]['pvca'].values[0] / days_in_current_month
    days_left = (date (current_date.year, current_date.month, days_in_current_month) - current_date).days
    res = average_daily_pvca * current_date.day + average_daily_pvca * days_left * 1.01
    return res

# функция которая модифицирует pva по дням - для текущего месяца плана
def modify_pva_current_month(plan_df, current_date, pva_coef):
    days_in_current_month = days_in_month(current_date.month, current_date.year)
    average_daily_pva = plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']==current_date.month]['pva'].values[0] / days_in_current_month
    days_left = (date (current_date.year, current_date.month, days_in_current_month) - current_date).days
    res = average_daily_pva * current_date.day + average_daily_pva * days_left * pva_coef
    return res

# функция которая корректирует план в зависимости от текущей даты и распроданости
def correct_plan(inp_plan_df, stock_df, current_date_string):
    # первым делом переведем дату из строки в формат datetime если на вход пришла строка
    if not isinstance(current_date_string, date):
        current_date = from_string_to_date(current_date_string)
    else:
        current_date = current_date_string
        
    current_pcvsop = scvhso_f(stock_df) # текущая распроданость
    plan_pcvsop = get_pcvsop_by_date(inp_plan_df, current_date) # плановая распроданость на текущую дату
    
    if current_pcvsop <= plan_pcvsop:
        return recalculate_plan_pcvsogap(calculate_plan_all(inp_plan_df),stock_df)
    else:
        plan_df = inp_plan_df.copy()
        plan_df['pvca'].values[plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']==current_date.month].index] = modify_pvca_current_month(plan_df, current_date)
        for i in range(plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']==current_date.month].index.values[0]+1, len(plan_df)):
            plan_df['pvca'].values[i] *= 1.01
        
        plan_pva_left = sum(plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']>=current_date.month]['pva'].values)+sum(plan_df.loc[plan_df['year']>current_date.year]['pva'].values)
        fact_pva_left = MEUA_f(stock_df)
        pva_coef = fact_pva_left / plan_pva_left 
        print(pva_coef)
        
        plan_df['pva'].values[plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']==current_date.month].index] = modify_pva_current_month(plan_df, current_date, pva_coef)
        for i in range(plan_df.loc[plan_df['year']==current_date.year].loc[plan_df['month']==current_date.month].index.values[0]+1, len(plan_df)):
            plan_df['pva'].values[i] *= pva_coef
        
        return recalculate_plan_pcvsogap(calculate_plan_all(plan_df),stock_df)
 
    #DMCSOCPAP_alt_f(recalculate_plan_pcvsogap(plan_df, current_pcvsop),current_pcvsop)