#!/usr/bin/env python3

from src.data_utils import *
from src.max_bcg import *

import pandas as pd

#Фунцкия для получения данных из таблицы по ключу и логину в конфиг файле
def reload_data(CONFIG_PATH):
    if not check_config(load_config(CONFIG_PATH)): # если с конфигом что-то не так или он отсутсвует вообще
        print('ERROR, inavlid config, or config not found')
    else:
        warehouse_df, looks_df, plans_df, buildings_set, income_df, class_df = load_data_from_sheets(load_config(CONFIG_PATH))  
        display_features = ['Дом', 'ID помещения', 'Номер помещения', 'Площадь, м2'] # колонки которые будут видны конечному пользователю
        display_dataframe = warehouse_df.filter(items=display_features) # отфильтруем таблицу для наглядного представления
        display_dataframe = display_dataframe.assign(BMMP='',BMMPRC='')
        return warehouse_df, looks_df, plans_df, buildings_set, income_df, display_dataframe, class_df#{'warehouse_df':warehouse_df, 'looks_df':looks_df, 'plans_df':plans_df, 'buildings_set':buildings_set, 'income_df':income_df, 'display_dataframe':display_dataframe}
        
#Функция для расчета цен базовой гипотезы для заданого дома - РАБОТАЕТ КОРРЕКТНО ТОЛЬКО ЕСЛИ ЕСТЬ НУЖНЫЕ СЛОВАРИ, нужно перед вызовом чекать дом на соответсвие требованиям
def process_basic(dataframe, visual_df, config):
    res = visual_df.copy()
    BMMP = BMMP_f(dataframe,config)
    BMMPRC = BMMPRC_f(dataframe,config)
    if 'BMMP' in  res:
        res['BMMP']=BMMP
    else:
        res.insert(len(res.columns),'BMMP', BMMP) 
    if 'BMMPRC' in res:
        res['BMMPRC']=BMMPRC
    else:
        res.insert(len(res.columns),'BMMPRC', BMMPRC) 
    return res
