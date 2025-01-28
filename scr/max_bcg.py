#!/usr/bin/env python3

# БАЗОВА ГІПОТЕЗА - по состоянию на 25.06.2021 тут все работает корректно, рекомендуется ничего не трогать и не менять

import pandas as pd
import math
import numpy as np


# Фактор поверху - обраний користувачем спосіб визначення міри цінності квартири (лінійно, степенево чи логарифмічно).
def BMSF_f(stock_df, config):
    BMSF = []
    if config['USER SWITCHES']['bpsms'] == 'LIN':
        maxfloor = max(stock_df['svsn'].values)
        max_ratio = float(config['BASIC HYPOTHESIS']['bpkfs'])+int(config['BASIC HYPOTHESIS']['bpbfs'])
        if max_ratio == 0 or maxfloor == 0:
            return [0]*len(stock_df)
        for i in range(0,len(stock_df)):
            cur_ratio = (stock_df['svsn'][i]/maxfloor)*float(config['BASIC HYPOTHESIS']['bpkfs'])+int(config['BASIC HYPOTHESIS']['bpbfs'])
            BMSF.append((cur_ratio/max_ratio)+((1-(cur_ratio/max_ratio))/float(config['BASIC HYPOTHESIS']['bpkfs'])))
        return BMSF
    elif config['USER SWITCHES']['bpsms'] == 'LOG':
        max_ratio = math.log(max(stock_df['svsn'].values),float(config['BASIC HYPOTHESIS']['bpffs']))+int(config['BASIC HYPOTHESIS']['bpbfs'])
        if max_ratio == 0:
            return [0]*len(stock_df)
        for i in range(0,len(stock_df)):
            cur_ratio = math.log(stock_df['svsn'][i],float(config['BASIC HYPOTHESIS']['bpffs']))+int(config['BASIC HYPOTHESIS']['bpbfs'])
            BMSF.append((cur_ratio/max_ratio)+((1-(cur_ratio/max_ratio))/float(config['BASIC HYPOTHESIS']['bpkfs'])))
        return BMSF
    elif config['USER SWITCHES']['bpsms'] == 'POW':
        max_ratio = (max(stock_df['svsn'].values)**float(config['BASIC HYPOTHESIS']['bpss']))+int(config['BASIC HYPOTHESIS']['bpbfs'])
        if max_ratio == 0:
            return [0]*len(stock_df)
        for i in range(0,len(stock_df)):
            cur_ratio = (stock_df['svsn'][i]**float(config['BASIC HYPOTHESIS']['bpss']))+int(config['BASIC HYPOTHESIS']['bpbfs'])
            BMSF.append((cur_ratio/max_ratio)+((1-(cur_ratio/max_ratio))/float(config['BASIC HYPOTHESIS']['bpkfs'])))
        return BMSF    
    else:
        print('unknown BPSMS value!')
        return 0

# Фактор площі - обраний користувачем спосіб визначення міри цінності квартири (лінійно, степенево чи логарифмічно).
def BMAF_f(stock_df, config):
    BMAF = []
    if config['USER SWITCHES']['bpams'] == 'LIN':
        min_ratio = (int(config['BASIC HYPOTHESIS']['bpbfa']) - scvmah_f(stock_df))/float(config['BASIC HYPOTHESIS']['bpkfa']) 
        if min_ratio == 0:
            return [0]*len(stock_df)
        for i in range(0,len(stock_df)):
            cur_ratio = (int(config['BASIC HYPOTHESIS']['bpbfa']) - stock_df['svta'][i])/float(config['BASIC HYPOTHESIS']['bpkfa']) 
            BMAF.append((cur_ratio/min_ratio)+((1-(cur_ratio/min_ratio))/float(config['BASIC HYPOTHESIS']['bpkfa'])))
        return BMAF
    elif config['USER SWITCHES']['bpams'] == 'LOG':
        max_ratio = math.log(min(stock_df['svta'].values),float(config['BASIC HYPOTHESIS']['bpffa']))+int(config['BASIC HYPOTHESIS']['bpbfa'])
        if max_ratio == 0:
            return [0]*len(stock_df)
        for i in range(0,len(stock_df)):
            cur_ratio = math.log(stock_df['svta'][i],float(config['BASIC HYPOTHESIS']['bpffa']))+int(config['BASIC HYPOTHESIS']['bpbfa'])
            BMAF.append((cur_ratio/max_ratio)+((1-(cur_ratio/max_ratio))/float(config['BASIC HYPOTHESIS']['bpkfa'])))
        return BMAF
    elif config['USER SWITCHES']['bpams'] == 'POW':
        max_ratio = 2**(float(config['BASIC HYPOTHESIS']['bpas'])*scvmah_f(stock_df))
        if max_ratio == 0:
            return [0]*len(stock_df)
        for i in range(0,len(stock_df)):
            cur_ratio = 2**(float(config['BASIC HYPOTHESIS']['bpas'])*stock_df['svta'][i])
            BMAF.append((cur_ratio/max_ratio)+((1-(cur_ratio/max_ratio))/float(config['BASIC HYPOTHESIS']['bpkfa'])))
        return BMAF    
    else:
        print('unknown BPAMS value!')
        return 0
    
# Фактор виду - Міра цінності квартири, обчислена у лінійній залежності від оцінки за вид звікна. Користувач самостійно задає параметри такої залежності    
def BMVF_f(stock_df, config):
    BMVF = []
    max_look = max(stock_df['svvw'].values)
    max_ratio = float(config['BASIC HYPOTHESIS']['bpkfv']) + int(config['BASIC HYPOTHESIS']['bpbfv'])
    if max_ratio == 0:
        return [0]*len(stock_df)
    for i in range(0,len(stock_df)):
        cur_ratio = (stock_df['svvw'][i]/max_look)*float(config['BASIC HYPOTHESIS']['bpkfv']) + int(config['BASIC HYPOTHESIS']['bpbfv'])
        BMVF.append(cur_ratio/max_ratio)
    return BMVF

# Фактор планування - Міра цінності квартири, обчислена у лінійній залежності від оцінки ергономіки планування. 
def BMPF_f(stock_df, config):
    BMPF = []
    max_design = max(stock_df['svpw'].values)
    max_ratio = float(config['BASIC HYPOTHESIS']['bpkfp']) + int(config['BASIC HYPOTHESIS']['bpbfp'])
    if max_ratio == 0:
        return [0]*len(stock_df)
    for i in range(0,len(stock_df)):
        cur_ratio = (stock_df['svpw'][i]/max_design)*float(config['BASIC HYPOTHESIS']['bpkfp']) + int(config['BASIC HYPOTHESIS']['bpbfp'])
        BMPF.append(cur_ratio/max_ratio)
    return BMPF

# Фактор рівня - Міра цінності квартири, від кількості рівнів (ярусів). 
def BMLF_f(stock_df, config):
    BMLF = []
    if float(config['BASIC HYPOTHESIS']['bptiik']) == 0:
        return [0]*len(stock_df)
    for i in range(0,len(stock_df)):
        BMLF.append(stock_df['svsq'][i]**(1/float(config['BASIC HYPOTHESIS']['bptiik'])))
    return BMLF

# Фактор терас - Міра цінності квартири, визначена від наявності терас. 
def BMTF_f(stock_df, config):
    BMTF = []
    if float(config['BASIC HYPOTHESIS']['bptik']) == 0:
        return [1]*len(stock_df)
    for i in range(0,len(stock_df)):
        if stock_df['svtq'][i] == 0:
            BMTF.append(2**(1/float(config['BASIC HYPOTHESIS']['bptik'])))
        else:
            BMTF.append(3**(1/float(config['BASIC HYPOTHESIS']['bptik'])))
    return BMTF

# обчислений скоринг цінності одиниці площі приміщення
def BMRS_f(stock_df, config):
    return (np.array(BMAF_f(stock_df,config)) * float(config['BASIC HYPOTHESIS']['bpav']) +
            np.array(BMVF_f(stock_df,config)) * float(config['BASIC HYPOTHESIS']['bpvv']) +
            np.array(BMSF_f(stock_df,config)) * float(config['BASIC HYPOTHESIS']['bpsv']) +
            np.array(BMLF_f(stock_df,config)) * float(config['BASIC HYPOTHESIS']['bptikw']) +
            np.array(BMPF_f(stock_df,config)) * float(config['BASIC HYPOTHESIS']['bppk']) +
            np.array(BMTF_f(stock_df,config)) * float(config['BASIC HYPOTHESIS']['bptkw']))

# умовна вартість приміщення
def BMRCV_f(stock_df,config):
    BMRS=BMRS_f(stock_df,config)
    BMRCV = []
    for i in range(0,len(stock_df)):
        BMRCV.append(BMRS[i]*stock_df['svta'][i])
    return BMRCV

# середньозважена умовна вартість приміщення по будинку
def BMRSWA_f(stock_df,config):
    return sum(BMRCV_f(stock_df,config))/sum(stock_df['svta'])

# Модельована ціна базової гіпотези - ціна м2. старту продажу приміщень, що розрахована у відповідності до базової цінової гіпотези відповідного будинку.
def BMMP_f(stock_df, config):
    BMMP = []
    BMRS = BMRS_f(stock_df,config)
    ratio = int(config['BASIC HYPOTHESIS']['bpbp'])/BMRSWA_f(stock_df,config)
    if scvmah_f(stock_df) == 0:
        return 0
    else:
        for i in range(0,len(stock_df)):
            BMMP.append(ratio*BMRS[i])
        return BMMP
    
# Вартість приміщеня на старті 
def BMMPRC_f(stock_df, config):
    BMMP = BMMP_f(stock_df, config)
    BMMPRC = []
    for i in range(0,len(stock_df)):
        BMMPRC.append(BMMP[i]*stock_df['svta'][i])
    return BMMPRC
    
# ф-ция возвращает минимальную площадь помещения для дома
def scvmah_f(stock_df): 
    if 'svta' in list(stock_df.columns):
        return min(stock_df['svta'].values)
    else:
        print('error. no svta data found!')
        return 0    

# ф-ция возвращает общую распроданость по всему дому
def scvhso_f(stock_df):
    if 'svsr' in list(stock_df.columns):
        return (len(stock_df.loc[stock_df['svsr']>0]) / len(stock_df))  
    else:
        print('error. no svsr data found!')
        return 0    