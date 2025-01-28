#!/usr/bin/env python3

import os
import gspread
import configparser
import math
import pandas as pd
import numpy as np
import random

from sklearn.utils import shuffle

from src.max_dp import *
from src.max_bcg import scvhso_f

# ф-ция убирает суммы продаж из таблицы STOCK
def preprocess_stock(stock_df):
    result_df = stock_df.copy()
    result_df['svsr'] = 0
    return result_df
    
# функция проверяет заполнены ли все параметры базовой гипотезы и динамического ценообразования, а также проверяет наличиес файла .credentias по нужному адресу
def check_config(config):
    if config == {} or not config:
        print ("config corrupted")
        return False
    section_names = ['PATH', 'BASIC HYPOTHESIS', 'USER SWITCHES', 'DYNAMIC PRICING']
    for section in section_names:
        if not section in config:
            print('не найдена одна или несколько секций, проверьте конфиг')
            print([v for v in config])
            return False
    basic_params = ['bpbp', 'bpav', 'bpvv', 'bpsv', 'bppk', 'bptikw', 'bptkw', 'bpas', 'bpffa', 'bpbfa', 'bpkfa', 'bpss', 'bpffs', 'bpbfs', 'bpkfs', 'bpkfv', 'bpbfv', 'bpkfp', 'bpbfp', 'bptiik', 'bptik']
    for par_name in basic_params:
        if not par_name in config['BASIC HYPOTHESIS']:
            print('не задан один или несколько параметров для БЦГ, проверьте конфиг')
            return False
    switches = [config['USER SWITCHES']['bpsms'],config['USER SWITCHES']['bpams']]
    for switch in switches:
        if not switch in ['LIN', 'LOG', 'POW']:
            print('переключаетлям установленны некорректные занчения, проверьте конфиг')
            return False
    dynamic_params = ['dpmf', 'dpccg', 'dpnb', 'dpss', 'dprs', 'dpps', 'dpvs', 'dpes', 'dpts', 'dpsb', 'dprb', 'dppb', 'dpvb', 'dpeb', 'dptb', 'dpol']
    for par_name in dynamic_params:
        if not par_name in config['DYNAMIC PRICING']:
            print('не задан один или несколько параметров для динамического ценообразования, проверьте конфиг')
            return False
    path_params = ['cred_file', 'key', 'warehouse_sheet', 'looks_sheet', 'plans_sheet', 'income_sheet', 'class_sheet']
    for par_name in path_params:
        if not par_name in config['PATH']:
            print('не задан один или несколько параметров пути к таблицам, проверьте конфиг')
            return False
    if not os.path.exists(config['PATH']['cred_file']):
        print ("путь к credentials указан неверно, не выходит обнарудить файл")
        return False
    else:
        print ("config - OK")
        return True
        
# функция проверяет есть ли файл конфига, и загружает его    
def load_config(path = 'config.ini'):
    if not os.path.exists(path):
        print ("путь к config указан неверно, не выходит обнаружить файл")
        return False
    #config_path = 'config_econom.ini'
    config = configparser.ConfigParser()
    config.read(path, encoding = 'utf-8')
    return config    

# функция для загрузки табличек с Складом, Словарем видов, словарем планировок
def load_data_from_sheets(config):
    gc = gspread.service_account(config['PATH']['cred_file']) # подгрузим credntials
    sh = gc.open_by_key(config['PATH']['key']) # откроем саму табличку
    
    temp_sheet = sh.worksheet(config['PATH']['warehouse_sheet']) # Листок "склад"
    warehouse_df = pd.DataFrame(temp_sheet.get_all_records()) # выгрузим все записи по проектам в таблицу
    temp_sheet = sh.worksheet(config['PATH']['looks_sheet']) # Листок со словарем ценностей видов из окна
    looks_df = pd.DataFrame(temp_sheet.get_all_records()) # выгрузим весь словарь ценностей видов в таблицу
    temp_sheet = sh.worksheet(config['PATH']['plans_sheet']) # Листок со словарем ценностей видов из окна
    plans_df = pd.DataFrame(temp_sheet.get_all_records()) # выгрузим весь словарь ценностей планировок в таблицу
    temp_sheet = sh.worksheet(config['PATH']['income_sheet']) # Листок со всеми планами продаж
    income_df = pd.DataFrame(temp_sheet.get_all_records()) # выгрузим весь словарь ценностей планировок в таблицу
    temp_sheet = sh.worksheet(config['PATH']['class_sheet']) # Листок со всеми классами ЖК и их базовыми ценами
    class_df = pd.DataFrame(temp_sheet.get_all_records())
    if 'Дом' in warehouse_df:
        buildings_set = set(warehouse_df['Дом'].values)
        return warehouse_df, looks_df, plans_df, buildings_set, income_df, class_df
    else:
        print('Колонка Дом не найдена в таблице!')
        return False

# фунция возвращает словарь ценностей видов для заданного дома
def reload_looks_worth(building_id, looks_df):
    temp_looks = looks_df.loc[looks_df['Будинок']==building_id]
    looks_worth = {}
    for i, value in enumerate(temp_looks['Види']):
        looks_worth[value] = temp_looks.loc[temp_looks['Види']==value]['цінність'].values[0]
    return looks_worth

# фунция возвращает словарь ценностей планировок для заданного дома
def reload_plans_worth(building_id, plans_df):
    temp_plans = plans_df.loc[plans_df['Будинок']==building_id]
    plans_worth = {}
    for i, value in enumerate(temp_plans['Види']):
        plans_worth[value] = temp_plans.loc[temp_plans['Види']==value]['цінність'].values[0]
    return plans_worth
    
# Функция для проверки есть ли для заданного дома таблицы ценностей видов и планировок (не пустые ли словари)
def check_looks_and_plans(building_id, looks_df, plans_df):
    if reload_looks_worth(building_id, looks_df) == {} or reload_plans_worth(building_id, plans_df) == {}:
        return False
    else:
        return True

# Функция для проверки есть ли для заданного дома в таблице информация о классе и базовой цене
def check_class_bpbp(building_id, class_df):
    building_class, building_bpbp = reload_class_bpbp(building_id, class_df)
    if building_class == '' or building_bpbp == '':
        return False
    else:
        return True

# фунция возвращает для заданного дома класс и базовую цену - в дальнейшем должна использоватся для автоматического выбора конфигов
def reload_class_bpbp(building_id, class_df):
    temp_df = class_df.loc[class_df['svh']==building_id]
    if temp_df['class'].values[0] and temp_df['BPBP'].values[0] :
        return temp_df['class'].values[0], temp_df['BPBP'].values[0] 
    else:
        return '',''

# функция возвращает все параметры необходимые для расчета плана для данного дома - в отличие от прошлой функции должна применятся для подсчета таблицы Income plan для тех домов для которых она изначально отстутсвует
def reload_plan_base_model(building_id, class_df):
    temp_df = class_df.loc[class_df['svh']==building_id]
    if temp_df['class'].values[0] and temp_df['BPBP'].values[0] and temp_df['start_year'].values[0] and temp_df['start_month'].values[0] and temp_df['duration_of_construction'].values[0] and temp_df['installment_min'].values[0] and temp_df['installment_max'].values[0] and temp_df['hansel_amount'].values[0] and temp_df['rate_of_return'].values[0] and temp_df['profitability_mode'].values[0]:
        return [temp_df['class'].values[0], temp_df['BPBP'].values[0], temp_df['start_year'].values[0], temp_df['start_month'].values[0], temp_df['duration_of_construction'].values[0], temp_df['installment_min'].values[0], temp_df['installment_max'].values[0], temp_df['hansel_amount'].values[0], temp_df['rate_of_return'].values[0], temp_df['profitability_mode'].values[0]]  
    else:
        return ['']*10

# Функция для проверки есть ли для заданного дома в таблице все параметры необходимые для расчета плана
def check_plan_base_model(building_id, class_df):
    base_pars = reload_plan_base_model(building_id, class_df)
    for par in base_pars:
        if par == '':
            return False
    return True

# функция которая возвращает таблицу STOCK по которой можно расчитать БЦГ, для заданного дома
def reload_stock_table(building_id, dataframe, looks_df, plans_df):
    
    df = dataframe.loc[dataframe['Дом']==building_id]
    lp_condition = check_looks_and_plans(building_id, looks_df, plans_df)
    if lp_condition:
        plans_worth = reload_plans_worth(building_id, plans_df)
        looks_worth = reload_looks_worth(building_id, looks_df)
    stock = {}
    stock['svid'] = [v for v in df['ID помещения'].values] # id
    stock['svrn'] = [v for v in df['Номер помещения'].values] # номер
    stock['svfp'] = [v for v in df['Полная цена'].values] # полная цена
    stock['svsn'] = [v for v in df['Этаж'].values] # этаж
    stock['sve'] = [v for v in df['Подъезд'].values] # подъезд
    stock['svun'] = [v for v in df['Номер на площадке'].values] # номер на площадке
    stock['svlc'] = [v for v in df['Название ЖК'].values] # название ЖК
    stock['svta'] = [v for v in df['Площадь, м2'].values] # площадь
    stock['svapp'] = [v for v in df['Цена за метр'].values] # цена м2
    stock['svrq'] = [v for v in df['Кол-во комнат'].values] # количество комнат
    stock['svpc'] = [v for v in df['Код планировки'].values] # код планировки
    stock['svvfw'] = [v for v in df['Куда выходят окна'].values] # вид из окна
    temp_list=[]
    for v in df['Кол-во балконов'].values:
        if v:
            temp_list.append(v)
        else:
            temp_list.append(0)
    stock['svbq'] = temp_list # кол-во балконов
    temp_list=[]
    for v in df['Количество уровней'].values:
        if v:
            temp_list.append(v)
        else:
            temp_list.append(1)
    stock['svsq'] = temp_list # количество уровней
    temp_list=[]
    for v in df['Кво терас'].values:
        if v:
            temp_list.append(v)
        else:
            temp_list.append(0)
    stock['svtq'] = temp_list # количество террас 
    stock['svh'] = [v for v in df['Дом'].values] # название дома
    temp_svsr=[]
    for v in df['Сума реализации'].values: # сумма реализации
        if v=='' or v==' ':
            temp_svsr.append(0)
        else:
            temp_svsr.append(int(v)) 
    stock['svsr'] = temp_svsr
    temp_list=[]
    if lp_condition:
        for v in df['Куда выходят окна'].values:
            temp_list.append(looks_worth[v])
    else:
        for v in df['Куда выходят окна'].values:
            temp_list.append(0)
    stock['svvw'] = temp_list # ценность видов из окна
    temp_list=[]
    if lp_condition:
        for v in df['Код планировки'].values:
            temp_list.append(plans_worth[v])
    else:
        for v in df['Куда выходят окна'].values:
            temp_list.append(0)
    stock['svpw'] = temp_list # ценность планировки
    # А ТАКЖЕ СРАЗУ СГРУППИРУЕМ ЭТАЖИ
    stock['scvsg']= [] # группа этажей
    min_floor = min (stock['svsn'])
    for i in range(0,len(stock['svsn'])):
        if stock['svsn'][i] == min_floor:
            stock['scvsg'].append(1) # для минимального этажа в доме группа = 1
        else:
            stock['scvsg'].append(1+math.ceil((stock['svsn'][i]-min_floor)/2)) # последующие группируем по два
    return pd.DataFrame(stock)

# функция которая возвращает таблицу PLAN по которой можно расчитать динамическое ценообразование для заданного дома
def reload_plan_table(building_id, dataframe):
    df = dataframe.loc[dataframe['Будинок']==building_id]
    plan = {}
    plan['pvh'] = [v for v in df['Будинок'].values] # id
    plan['pvp'] = [v for v in df['Project'].values] # проект
    plan['pva'] = [v for v in df['Area'].values] # плановая площадь
    plan['pvca'] = [v for v in df['Contract amount'].values] # плановая сумма продаж
    #plan['pvd'] = [] # дата
    plan['year'] = [v for v in df['Year'].values] # год
    plan['month'] = [v for v in df['Months'].values] # месяц
    return pd.DataFrame(plan).sort_values(by=['year','month'])

# функция для подсчета расчетных значений таблицы stock (для динамического ценообразования)
def calculate_stock(stock_df):
    scvsop = [] # распроданость по планировкам
    scvsol = [] # распроданость по видам из окна
    scvsosg = [] # распроданость по группам этажей
    scvsorq = [] # распроданость по кол-ву комнат
    scvsoe = [] # распроданость по подъездам
    scvsot = [] # распроданость по наличию террасы
    
    scvdcp = [] # диф потенциал по ценам
    
    stock_scvsop = scvsop_f(stock_df) # словарь распроданости по планировкам
    stock_scvsol = scvsol_f(stock_df) # словарь распроданости по видам из окна
    stock_scvsosg = scvsosg_f(stock_df) # словарь распроданости по группам этажей
    stock_scvsorq = scvsorq_f(stock_df) # словарь распроданости по количеству комнат
    stock_scvsoe = scvsoe_f(stock_df) # словарь распроданости по подъездам
    stock_scvsot = scvsot_f(stock_df) # словарь распроданости по статусу наличия террасы
    #print([v for v in stock_scvsot])
    fp_sum = sum(stock_df['svfp'].values) # сумма всех цен для подсчета ДПЦ
    ta_sum = sum(stock_df['svta'].values) # сумма всех площадей для подсчета ДПЦ
    
    for i in range(0,len(stock_df)):
        scvsop.append(stock_scvsop[stock_df['svpc'][i]]) # распроданость по планировке
        scvsol.append(stock_scvsol[stock_df['svvfw'][i]]) # распроданость по виду из окна
        scvsosg.append(stock_scvsosg[stock_df['scvsg'][i]]) # распроданость по группе этажа
        scvsorq.append(stock_scvsorq[stock_df['svrq'][i]]) # распроданость по количеству комнат
        scvsoe.append(stock_scvsoe[stock_df['sve'][i]]) # распроданость по подъездам
        if (stock_df['svtq'][i] == 0):
            scvsot.append(stock_scvsot['0']) # распроданость помещений без террас
        else:
            scvsot.append(stock_scvsot['1']) # распроданость помещений с террасами
        if stock_df['svapp'][i] == 0:
            scvdcp.append(0)
        else:
            scvdcp.append(stock_df['svapp'][i]*ta_sum/fp_sum) # дифф потенциал по ценам
    
    result_df = stock_df.copy()
    result_df.insert(len(result_df.columns),'scvsop', scvsop) 
    result_df.insert(len(result_df.columns),'scvsol', scvsol)  
    result_df.insert(len(result_df.columns),'scvsosg', scvsosg)  
    result_df.insert(len(result_df.columns),'scvsorq', scvsorq)
    result_df.insert(len(result_df.columns),'scvsoe', scvsoe)
    result_df.insert(len(result_df.columns),'scvsot', scvsot)
    result_df.insert(len(result_df.columns),'scvdcp', scvdcp)
    return result_df

# фунция возвращает план продаж для заданного дома
def load_income_plan(building_id, income_df):
    temp_income = income_df.loc[income_df['Будинок']==building_id]
    if len(temp_income)>0:
        return temp_income
    else:
        return []

# функція для отримання поточної суми вартостей продажу
def get_pcvrtrp_from_plan(plan_df):
    target_gap = max(plan_df.loc[plan_df['pcvsogap'] <= 0]['pcvsogap'].values)
    return min(plan_df.loc[plan_df['pcvsogap'] == target_gap]['pcvrtrp'])

# функция для подсчета расчетных значений таблицы plan (для динамического ценообразования) - 31.08.21 - ЗАМЕНЕНО НА БОЛЕЕ НОВІЙ ВАРИАНТ (см. ниже)
def calculate_plan(plan_df, stock_df, update = False):

    pcvrtap = [] #  планова сума проданих площ
    pcvrtrp = [] # планова сума підписань
    pcvrtapp = [] # планова накопичена середня ціна 
    pcvcp = [] # планова сума вартостей продажу
    pcvapp = [] # планова середня поточна 
    pcvsop = [] # план розпроданості будинку у залежності від періоду
    pcvsogap = [] # розрив між поточною і плановою розпроданістю будинку
    
    pcvsoh = scvhso_f(stock_df) # значення поточної розпроданості будинку
    total_plan_area = sum(plan_df['pva'].values)
    current_pcvrtap = 0
    current_pcvrtrp = 0
    
    for i in range(0,len(plan_df)):
        current_pcvrtap += plan_df['pva'][i] # добавляем текущую площадь к суме
        pcvrtap.append(current_pcvrtap) #  планова сума проданих площ
        current_pcvrtrp += plan_df['pvca'][i] # добавляем текущую суму продаж к общей суме
        pcvrtrp.append(current_pcvrtrp) # общая сума продаж
        if not current_pcvrtap == 0:
            pcvrtapp.append(current_pcvrtrp/current_pcvrtap) # накопичена середня ціна 
            pcvcp.append(total_plan_area * (current_pcvrtrp/current_pcvrtap)) # планова сума вартостей продажу
        else:
            print('cur_PCVTRP == 0!!')
            pcvrtapp.append(0)
            pcvcp.append(0)    
        if not plan_df['pva'][i] == 0:
            pcvapp.append(plan_df['pvca'][i]/plan_df['pva'][i]) # планова середня поточна 
        else:
            pcvapp.append(pcvapp[i-1])
        pcvsop.append(current_pcvrtap/total_plan_area) # план розпроданості будинку у залежності від періоду
        pcvsogap.append(pcvsoh - (current_pcvrtap/total_plan_area))
    if update == False:
        result_df = plan_df.copy()
        result_df.insert(len(result_df.columns),'pcvrtap', pcvrtap) 
        result_df.insert(len(result_df.columns),'pcvrtrp', pcvrtrp) 
        result_df.insert(len(result_df.columns),'pcvrtapp', pcvrtapp)
        result_df.insert(len(result_df.columns),'pcvcp', pcvcp)
        result_df.insert(len(result_df.columns),'pcvapp', pcvapp)
        result_df.insert(len(result_df.columns),'pcvsop', pcvsop)
        result_df.insert(len(result_df.columns),'pcvsogap', pcvsogap)
        return result_df
    else:
        plan_df['pcvrtap'] = pcvrtap
        plan_df['pcvrtrp'] = pcvrtrp
        plan_df['pcvrtapp'] = pcvrtapp
        plan_df['pcvcp'] = pcvcp
        plan_df['pcvapp'] = pcvapp
        plan_df['pcvsop'] = pcvsop
        plan_df['pcvsogap'] = pcvsogap
        return plan_df

############################ НОВЫЕ ФУНКЦИИ ДЛЯ ПОДСЧЕТА\ПЕРЕСЧЕТА ПЛАНА - добавлено 31.08.21
# подсчет всего кроме pcvsogap - по задумке применяем 1 раз
##
# функция для подсчета расчетных значений таблицы plan на основе конкретного процента распроданости hso
def calculate_plan_all(plan_df):

    pcvrtap = [] #  планова сума проданих площ
    pcvrtrp = [] # планова сума підписань
    pcvrtapp = [] # планова накопичена середня ціна 
    pcvcp = [] # планова сума вартостей продажу
    pcvapp = [] # планова середня поточна 
    pcvsop = [] # план розпроданості будинку у залежності від періоду
    pcvapp_end=[] # планова середня поточна станом на кінець періоду 
    total_plan_area = sum(plan_df['pva'].values)
    current_pcvrtap = 0
    current_pcvrtrp = 0
    for i in range(0,len(plan_df)):
        current_pcvrtap += plan_df['pva'][i] # добавляем текущую площадь к суме
        pcvrtap.append(current_pcvrtap) #  планова сума проданих площ
        current_pcvrtrp += plan_df['pvca'][i] # добавляем текущую суму продаж к общей суме
        pcvrtrp.append(current_pcvrtrp) # общая сума продаж
        if not current_pcvrtap == 0:
            pcvrtapp.append(current_pcvrtrp/current_pcvrtap) # накопичена середня ціна 
            pcvcp.append(total_plan_area * (current_pcvrtrp/current_pcvrtap)) # планова сума вартостей продажу
        else:
            print('cur_PCVTRP == 0!!')
            pcvrtapp.append(0)
            pcvcp.append(0)    
        if not plan_df['pva'][i] == 0:
            pcvapp.append(plan_df['pvca'][i]/plan_df['pva'][i]) # планова середня поточна 
        else:
            pcvapp.append(pcvapp[i-1])
        pcvsop.append(current_pcvrtap/total_plan_area) # план розпроданості будинку у залежності від періоду
    for i in range(0,len(plan_df)-1):
        pcvapp_end.append((pcvapp[i]+pcvapp[i+1])/2)
    pcvapp_end.append(pcvapp[-1]*(pcvapp[-1]/pcvapp[-2]))
    if not 'pcvrtap' in plan_df.columns:
        result_df = plan_df.copy()
        result_df.insert(len(result_df.columns),'pcvrtap', pcvrtap) 
        result_df.insert(len(result_df.columns),'pcvrtrp', pcvrtrp) 
        result_df.insert(len(result_df.columns),'pcvrtapp', pcvrtapp)
        result_df.insert(len(result_df.columns),'pcvcp', pcvcp)
        result_df.insert(len(result_df.columns),'pcvapp', pcvapp)
        result_df.insert(len(result_df.columns),'pcvapp_end', pcvapp_end)
        result_df.insert(len(result_df.columns),'pcvsop', pcvsop)
        return result_df
    else:
        plan_df['pcvrtap'] = pcvrtap
        plan_df['pcvrtrp'] = pcvrtrp
        plan_df['pcvrtapp'] = pcvrtapp
        plan_df['pcvcp'] = pcvcp
        plan_df['pcvapp'] = pcvapp
        plan_df['pcvapp_end'] = pcvapp_end
        plan_df['pcvsop'] = pcvsop
        return plan_df
##
# подсчет только pcvsogap - применяем каждую итерацию
def recalculate_plan_pcvsogap(plan_df, stock_df):
    pcvsogap = [] # розрив між поточною і плановою розпроданістю будинку
    pcvsoh = scvhso_f(stock_df) # значення поточної розпроданості будинку
    total_plan_area = sum(plan_df['pva'].values)
    for i in range(0,len(plan_df)):
        pcvsogap.append(pcvsoh - (plan_df['pcvrtap'][i]/total_plan_area))
    if not 'pcvsogap' in plan_df.columns:
        result_df = plan_df.copy()
        result_df.insert(len(result_df.columns),'pcvsogap', pcvsogap)
        return result_df
    else:
        plan_df['pcvsogap'] = pcvsogap
        return plan_df
##
#######################################################


# Функция которая подготавливает случайній список продажи квартир по порядку       
def get_random_sales_list(df, building_id):
    return list(shuffle(df.loc[df['svh']==building_id]['svid'].values))
    
# функция для проверки есть ли проданные помещения в доме     
def check_stock_svsr(stock_df):
    if len(stock_df.loc[stock_df['svsr']>0]) == 0:
        return False
    else:
        return True
        
        
# функция делает таблицу айди помещений рассортированных в зависимости от этажа, подъезда номера на лестн клетке итд
def custom_id_table(stock):
    floor_entrance_tuples = []
    rooms_list = sorted(list(set(stock['svun'])))
    rooms_data = {}
    for floor in sorted(list(set(stock['svsn']))):
        for entrance in sorted(list(set(stock['sve']))):
            floor_entrance_tuples.append((floor,entrance))
            for room in rooms_list:
                if not room in rooms_data.keys():
                    rooms_data[room]=[]
                temp_df=stock[stock['svsn']==floor][stock['sve']==entrance][stock['svun']==room]
                if len(temp_df['svid'].values)>0:
                    rooms_data[room].append(temp_df['svid'].values[0])
                else:
                    rooms_data[room].append(0)
    index = pd.MultiIndex.from_tuples(floor_entrance_tuples)
    print(rooms_data)
  
    df = pd.DataFrame(data = rooms_data, index = index, columns = rooms_list)
    return df

# функция берет две таблицы и заменяетв одной айдишки на значение параметра par_name соответсвтующее этим айдишкам из другой таблицы
def transfer_par(table1, table2, id_field_name, par_name):
    res_table = table1.copy()
    for row in table1:
        for i, v in enumerate(table1[row].values):
            if not v ==0:
                res_table[row][i]=table2[table2[id_field_name]==v][par_name].values[0]
    for v in res_table:
        res_table[v] = pd.to_numeric(res_table[v], downcast="float")
    return res_table

# функция считает и отправляет пользователю хитмап
def get_heatmap(stock, obj_table, id_field_name, obj_par_name, savename):
    id_table = custom_id_table(stock)
    #sns.set(rc={'figure.figsize':(11.7,8.27)})
    mtr = transfer_par(id_table, obj_table, id_field_name, obj_par_name)
    #ax = sns.heatmap(mtr, annot=True, fmt="f")
    #ax.set(ylabel='Этаж-Подъезд', xlabel='Номер на лестничной площадке', title = 'Цены помещений')
    #return ax.figure.savefig(str(savename)+"heatmap_output.png")
    return mtr
    
# функция которая возвращает id помещения случайно выбраное из лучших кандидатов (РАЦИОНАЛЬНІЙ ПОКУПАТЕЛЬ)
def get_candidate_id_from_stock(stock):
    temp_stock = stock.loc[stock['svsr']==0].copy() # рассмотрим только не проданіе квартиры
    full_prices = sorted(set(temp_stock['svfp'].values)) # список уникальных полных цен помещений
    if len(full_prices)<=5: # уникальных полных цен осталось 5 или меньше - выбираем 1 кандидата случайно из всех
        candidate_id_list = temp_stock['svid'].values
        
    elif len(full_prices)<50: # уникальных полных цен осталось 50 или меньше - выбирае 1 кандидата случайно из 5 наиболее дешевых 
        candidate_price_list = sorted(set(temp_stock['svfp'].values))[:5]
        candidate_id_list = temp_stock.loc[temp_stock['svfp'].isin(candidate_price_list)]['svid'].values
        
    else: # уникальных полных цен осталось больше 50 - выбираем 1 кандидата случайно из 10% наиболее дешевых
        candidate_price_list = sorted(set(temp_stock['svfp'].values))[:len(set(temp_stock['svfp'].values))//10] 
        candidate_id_list = temp_stock.loc[temp_stock['svfp'].isin(candidate_price_list)]['svid'].values
    
    return candidate_id_list[int(random.random()*len(candidate_id_list)//1)] 

# функция которая возвращает id помещения случайно выбраное из лучших кандидатов (!NEW! РАЦИОНАЛЬНІЙ ПОКУПАТЕЛЬ !NEW!)
def get_candidate_id_from_stock_new(stock):
    temp_stock = stock.loc[stock['svsr']==0].copy() # рассмотрим только не проданіе квартиры
    if len(temp_stock['svid'].values)<=10: # уникальных полных цен осталось 12 или меньше - выбираем 1 кандидата случайно из всех
        candidate_id_list = temp_stock['svid'].values    
    else: # уникальных полных цен осталось больше 10 - выбираем 10 кандидатов и случайно вібираем 1го из них
        percentile_25 = np.percentile(temp_stock['svfp'].values,25)
        percentile_50 = np.percentile(temp_stock['svfp'].values,50)
        percentile_75 = np.percentile(temp_stock['svfp'].values,75)
        candidate_id_list = []
        tmp = temp_stock.loc[temp_stock['svfp']<=percentile_25].loc[temp_stock['svfp']>0]['svid'].values
        for i in range(1,5): # четыре помещения 25го процентиля
            candidate_id_list.append(tmp[int(random.random()*len(tmp)//1)])
        tmp = temp_stock.loc[temp_stock['svfp']<=percentile_50].loc[temp_stock['svfp']>percentile_25]['svid'].values
        for i in range(1,4): # три помещения 50го процентиля
            candidate_id_list.append(tmp[int(random.random()*len(tmp)//1)])
        tmp = temp_stock.loc[temp_stock['svfp']<=percentile_75].loc[temp_stock['svfp']>percentile_50]['svid'].values
        for i in range(1,3): # два помещения 75го процентиля
            candidate_id_list.append(tmp[int(random.random()*len(tmp)//1)])
        tmp = temp_stock.loc[temp_stock['svfp']>percentile_75]['svid'].values
        candidate_id_list.append(tmp[int(random.random()*len(tmp)//1)]) # одно помещение 100го процентиля
            
    return candidate_id_list[int(random.random()*len(candidate_id_list)//1)]  

# функция которая возвращает id помещения случайно выбраное из всех кандидатов (НЕРАЦИОНАЛЬНІЙ ПОКУПАТЕЛЬ)
def get_random_id_from_stock(stock):
    temp_stock = stock.loc[stock['svsr']==0].copy() # рассмотрим только не проданіе квартиры
    candidate_id_list = temp_stock['svid'].values
    return candidate_id_list[int(random.random()*len(candidate_id_list)//1)] 

# для террас функция которая возвращает 1 если в доме нет террас и 2 если есть квартиры с террасами
def get_terrace_q(stock):
    if len(list( set(stock['svtq'].values) ))>=2:
        return 2
    else:
        return 1