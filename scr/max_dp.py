#!/usr/bin/env python3

import pandas as pd
import numpy as np
from src.max_bcg import scvhso_f, BMRS_f
'''
Динамическое ценообразование
'''
# СЛОВАРИ РАСПРОДАНОСТЕЙ 

# ф-ция возвращает словарь распроданости по планировкам
def scvsop_f(stock_df):
    scvsop = {}
    if 'svpc' in list(stock_df.columns):
        for pc in set(stock_df['svpc'].values):
            scvsop[pc] = (len(stock_df.loc[stock_df['svpc']==pc].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['svpc']==pc]))
        return scvsop    
    else:
        print('error. no svpc data found!')
        return 0
    
# ф-ция возвращает словарь распроданости по видам из окна
def scvsol_f(stock_df):
    scvsol = {}
    if 'svvfw' in list(stock_df.columns):
        for vfw in set(stock_df['svvfw'].values):
            scvsol[vfw] = (len(stock_df.loc[stock_df['svvfw']==vfw].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['svvfw']==vfw]))
        return scvsol    
    else:
        print('error. no svvfw data found!')
        return 0
    
# ф-ция возвращает словарь распроданости по группам этажей
def scvsosg_f(stock_df):
    scvsosg = {}
    if 'scvsg' in list(stock_df.columns):
        for sg in set(stock_df['scvsg'].values):
            scvsosg[sg] = (len(stock_df.loc[stock_df['scvsg']==sg].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['scvsg']==sg]))
        return scvsosg    
    else:
        print('error. no scvsg data found!')
        return 0      

# ф-ция возвращает словарь распроданости по кол-ву комнат
def scvsorq_f(stock_df):
    scvsorq = {}
    if 'svrq' in list(stock_df.columns):
        for rq in set(stock_df['svrq'].values):
            scvsorq[rq] = (len(stock_df.loc[stock_df['svrq']==rq].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['svrq']==rq]))
        return scvsorq    
    else:
        print('error. no svrq data found!')
        return 0   
    
# ф-ция возвращает словарь распроданости по подъездам
def scvsoe_f(stock_df):
    scvsoe = {}
    if 'sve' in list(stock_df.columns):
        for e in set(stock_df['sve'].values):
            scvsoe[e] = (len(stock_df.loc[stock_df['sve']==e].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['sve']==e]))
        return scvsoe    
    else:
        print('error. no sve data found!')
        return 0   
    
# ф-ция возвращает словарь распроданости по статусу наличия террасы
def scvsot_f(stock_df):
    scvsot = {}
    if 'svtq' in list(stock_df.columns):
        if len(stock_df.loc[stock_df['svtq']==0]) == 0 or len(stock_df.loc[stock_df['svtq']>0]) == 0:
            scvsot['0'] = scvsot['1'] = 0
        else:
            scvsot['0'] = (len(stock_df.loc[stock_df['svtq']==0].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['svtq']==0]))
            scvsot['1'] = (len(stock_df.loc[stock_df['svtq']>0].loc[stock_df['svsr']>0]) / len(stock_df.loc[stock_df['svtq']>0]))
        return scvsot    
    else:
        print('error. no svtq data found!')
        return 0    
    
    
# визначення середніх планових цін продажу, возвращает pcvsodr_1 и pcvsodr_2 - изм. 31.08.21
def pcvsodr_f (plan_df):
    if len(plan_df.loc[plan_df['pcvsogap']>=0]['pcvsogap'].values) == 0:
        return [plan_df.loc[plan_df['pcvsogap']==max(plan_df.loc[plan_df['pcvsogap']<0]['pcvsogap'].values)]['pcvapp_end'].values[0]]*2
    elif len(plan_df.loc[plan_df['pcvsogap']<0]['pcvsogap'].values) == 0:
        return [plan_df.loc[plan_df['pcvsogap']==min(plan_df.loc[plan_df['pcvsogap']>=0]['pcvsogap'].values)]['pcvapp_end'].values[0]]*2
    else:
        pcvsogap_1 = min(plan_df.loc[plan_df['pcvsogap']>=0]['pcvsogap'].values)
        pcvsogap_2 = max(plan_df.loc[plan_df['pcvsogap']<0]['pcvsogap'].values)
        pcvsodr_1 = plan_df.loc[plan_df['pcvsogap']==pcvsogap_1]['pcvapp_end'].values[0]
        pcvsodr_2 = plan_df.loc[plan_df['pcvsogap']==pcvsogap_2]['pcvapp_end'].values[0]
        return [pcvsodr_1, pcvsodr_2]
    
# розпроданості будинку у залежності від періоду, возвращает pcvsop_1 и pcvsop_2
def pcvsop_f (plan_df):
    if len(plan_df.loc[plan_df['pcvsogap']>=0]['pcvsogap'].values) == 0:
        return [plan_df.loc[plan_df['pcvsogap']==max(plan_df.loc[plan_df['pcvsogap']<0]['pcvsogap'].values)]['pcvsop'].values[0]]*2
    elif len(plan_df.loc[plan_df['pcvsogap']<0]['pcvsogap'].values) == 0:
        return [plan_df.loc[plan_df['pcvsogap']==min(plan_df.loc[plan_df['pcvsogap']>=0]['pcvsogap'].values)]['pcvsop'].values[0]]*2
    else:
        pcvsogap_1 = min(plan_df.loc[plan_df['pcvsogap']>=0]['pcvsogap'].values)
        pcvsogap_2 = max(plan_df.loc[plan_df['pcvsogap']<0]['pcvsogap'].values)
        pcvsop_1 = plan_df.loc[plan_df['pcvsogap']==pcvsogap_1]['pcvsop'].values[0]
        pcvsop_2 = plan_df.loc[plan_df['pcvsogap']==pcvsogap_2]['pcvsop'].values[0]
        return [pcvsop_1, pcvsop_2]

# ДИНАМІЧНЕ ЦІНОУТВОРЕННЯ
# Виручка по реалізованим
def MSVSR_f(stock_df):
    return sum(stock_df['svsr'])

# Вартість вільних приміщень - ДОДАНО 26.08.2021
def MSVSE_f(stock_df):
    return sum(stock_df.loc[stock_df['svsr']==0]['svfp'])

# Площа по реалізованим
def MRUA_f(stock_df):
    return sum(stock_df.loc[stock_df['svsr']>0]['svta'])

# Середня по реалізованим
def MRUAP_f(stock_df):
    if MRUA_f(stock_df) == 0:
        return 0
    else:
        return MSVSR_f(stock_df)/MRUA_f(stock_df)

# Площа вільних приміщень
def MEUA_f(stock_df):
    return sum(stock_df.loc[stock_df['svsr']==0]['svta'])

# Площа проданих приміщень 10.08.2021
def MEUS_f(stock_df):
    return sum(stock_df.loc[stock_df['svsr']>0]['svta'])

# Поточна планова середня розрахована від рівня розпроданості - обновлено 31.08.21
def DMCSOCPAP_f(stock_df,plan_df):
    
    if max(pcvsop_f(plan_df)) == min(pcvsop_f(plan_df)): # обработка "хвостика"
        end_pcvapp = plan_df['pcvapp'].values[-1] # цена соответсвующая распроданости в 1
        start_pcvapp = plan_df['pcvapp'].values[0] # цена соответсвующая распроданости первого месяца
        start_pcvsop = plan_df['pcvsop'].values[0] # распроданость первого месяца
        # теперь будем считать через подобные треугольнички (сначала построим треугольничек найдя нижний угол):
        y_0 = start_pcvapp - ((end_pcvapp - start_pcvapp)/(1-start_pcvsop))*start_pcvsop
        # теперь внутрии треугольника найдем нужную линию и возвратим ответ
        return y_0 + ((start_pcvapp - y_0)/(start_pcvsop)*scvhso_f(stock_df))
        # return min(pcvsodr_f(plan_df)) # костіль т.к. должен быть "нулевой месяц" - использовался до 31.08.2021го
    else:
        return min(pcvsodr_f(plan_df))+((scvhso_f(stock_df)-min(pcvsop_f(plan_df)))/(max(pcvsop_f(plan_df))-min(pcvsop_f(plan_df))))*(max(pcvsodr_f(plan_df))-min(pcvsodr_f(plan_df)))
        
# Компенсована поточна середня
def MCAPP_f(stock_df,plan_df,config):
    return DMCSOCPAP_f(stock_df,plan_df)+int(config['DYNAMIC PRICING']['dpccg'])

# Вартість залишку у цінах планової середньї
def DMESE_f(stock_df,plan_df,config):
    return MCAPP_f(stock_df,plan_df,config)*MEUA_f(stock_df)

# СЛОВАРИ ПЕРЕПРОДАНОСТЕЙ 

# Значення поточноЇ перепроданості приміщень, приналежних відповідному підїзду
def DMOSE_f(stock_df):
    if scvhso_f(stock_df) == 0:
        return scvsoe_f(stock_df)
    else:
        temp = scvsoe_f(stock_df)
        hso = scvhso_f(stock_df)
        for key in temp:    
            temp[key] /=  hso
        return temp
    
# Значення поточноЇ перепроданості приміщень, з відповідним видом з вікна
def DMOSL_f(stock_df):
    if scvhso_f(stock_df) == 0:
        return scvsol_f(stock_df)
    else:
        temp = scvsol_f(stock_df)
        hso = scvhso_f(stock_df)
        for key in temp:    
            temp[key] /=  hso
        return temp   
    
# Значення поточноЇ перепроданості приміщень, приналежних відповідному планувальному рішенню
def DMOSP_f(stock_df):
    if scvhso_f(stock_df) == 0:
        return scvsop_f(stock_df)
    else:
        temp = scvsop_f(stock_df)
        hso = scvhso_f(stock_df)
        for key in temp:    
            temp[key] /=  hso
        return temp
    
# Значення поточноЇ перепроданості приміщень, з відповідною кількостю кімнат
def DMOSRQ_f(stock_df):
    if scvhso_f(stock_df) == 0:
        return scvsorq_f(stock_df)
    else:
        temp = scvsorq_f(stock_df)
        hso = scvhso_f(stock_df)
        for key in temp:    
            temp[key] /=  hso
        return temp
    
# Значення поточноЇ перепроданості приміщень, приналежних відповідній групі поверхів
def DMOSSG_f(stock_df):
    if scvhso_f(stock_df) == 0:
        return scvsosg_f(stock_df)
    else:
        temp = scvsosg_f(stock_df)
        hso = scvhso_f(stock_df)
        for key in temp:    
            temp[key] /=  hso
        return temp
    
# Значення поточноЇ перепроданості приміщень, в залежності від наявності чи кількості терас
def DMOST_f(stock_df):
    if scvhso_f(stock_df) == 0:
        return scvsot_f(stock_df)
    else:
        temp = scvsot_f(stock_df)
        hso = scvhso_f(stock_df)
        for key in temp:    
            temp[key] /=  hso
        return temp
    
# Нараховані бали цінності приміщень відповідного планування згідно його пепроданості, обчислене через квадратичну функцію де її викривлення користувач задає через відповідний параметр DP*S
def DMPS_f(stock_df, config):
    temp = DMOSP_f(stock_df)
    for key in temp:
        temp[key] = (int(config['DYNAMIC PRICING']['dppb'])+
                     (int(config['DYNAMIC PRICING']['dppb'])*(temp[key]**(1/float(config['DYNAMIC PRICING']['dpps'])))))
    return temp

# Нараховані бали цінності приміщень з відповідним видом з вікон, згідно його пепроданості, обчислене через квадратичну функцію де її викривлення користувач задає через відповідний параметр DP*S   
def DMVS_f(stock_df, config):
    temp = DMOSL_f(stock_df)
    for key in temp:
        temp[key] = (int(config['DYNAMIC PRICING']['dpvb'])+
                     (int(config['DYNAMIC PRICING']['dpvb'])*(temp[key]**(1/float(config['DYNAMIC PRICING']['dpvs'])))))
    return temp

# Нараховані бали цінності приміщень відповідно наявної кількості кімнати, згідно пепроданості, обчислене через квадратичну функцію де її викривлення користувач задає через відповідний параметр DP*S
def DMPRS_f(stock_df, config):
    temp = DMOSRQ_f(stock_df)
    for key in temp:
        temp[key] = (int(config['DYNAMIC PRICING']['dprb'])+
                     (int(config['DYNAMIC PRICING']['dprb'])*(temp[key]**(1/float(config['DYNAMIC PRICING']['dprs'])))))
    return temp

# Нараховані бали цінності приміщень відповідного підїзду у якому воно знаходиться, згідно його пепроданості, обчислене через квадратичну функцію де її викривлення користувач задає через відповідний параметр DP*S
def DMES_f(stock_df, config):
    temp = DMOSE_f(stock_df)
    for key in temp:
        temp[key] = (int(config['DYNAMIC PRICING']['dpeb'])+
                     (int(config['DYNAMIC PRICING']['dpeb'])*(temp[key]**(1/float(config['DYNAMIC PRICING']['dpes'])))))
    return temp

# Нараховані бали цінності приміщень відповідного групи повехрів у якому воно знаходиться, згідно їх пепроданості, обчислене через квадратичну функцію де її викривлення користувач задає через відповідний параметр DP*S
def DMSGS_f(stock_df, config):
    temp = DMOSSG_f(stock_df)
    for key in temp:
        temp[key] = (int(config['DYNAMIC PRICING']['dpsb'])+
                     (int(config['DYNAMIC PRICING']['dpsb'])*(temp[key]**(1/float(config['DYNAMIC PRICING']['dpss'])))))
    return temp

# Нараховані бали цінності приміщень відповідно наявності тераси чи їх кількості, згідно їх пепроданості, обчислене через квадратичну функцію де її викривлення користувач задає через відповідний параметр DP*S
def DMTS_f(stock_df, config):
    temp = DMOST_f(stock_df)
    for key in temp:
        temp[key] = (int(config['DYNAMIC PRICING']['dptb'])+
                     (int(config['DYNAMIC PRICING']['dptb'])*(temp[key]**(1/float(config['DYNAMIC PRICING']['dpts'])))))
    return temp

# Нараховані бали цінності приміщень динамічної моделі
def DMWDP_f(stock_df,config):
    DMVS = DMVS_f(stock_df, config)
    DMPRS = DMPRS_f(stock_df, config)
    DMPS = DMPS_f(stock_df, config)
    DMSGS = DMSGS_f(stock_df, config)
    DMES = DMES_f(stock_df, config)
    DMTS = DMTS_f(stock_df, config)
    DMWDP = []
    for i in range(0,len(stock_df)):
        if stock_df['svsr'][i] == 0:
            DMWDP_t = (DMVS[stock_df['svvfw'][i]] + DMPRS[stock_df['svrq'][i]] + DMPS[stock_df['svpc'][i]] + 
                       DMSGS[stock_df['scvsg'][i]] + DMES[stock_df['sve'][i]])
            if stock_df['svtq'][i] > 0 :
                DMWDP_t += DMTS['1']
            else:
                DMWDP_t += DMTS['0']
        else:
            DMWDP_t = 0 # для проданных помещений считаем сумму баллов ценности равной нулю
        DMWDP.append(DMWDP_t)
    return DMWDP

# Нараховані бали цінності приміщень динамічної моделі СТИСНУТА 11.08.2021
def DMWDPS_f(stock_df,config):
    BMRS = BMRS_f(stock_df, config)
    spread = (max(BMRS)-min(BMRS))/max(BMRS)
    DMWDP = DMWDP_f(stock_df, config)
    DMWDP_med = np.median([v for v in DMWDP if not v == 0])
    DMWDP_max = max(DMWDP)
    DMWDP_min = min(DMWDP)
    DMWDPS = []
    #if DMWDP_med == 0:
    #    print('oopse median is 0')
    #    print(DMWDP)
    for v in DMWDP:
        if v == 0:
            DMWDPS.append(0)
        else:
            dif = (DMWDP_med-v)/DMWDP_med
            if np.abs(dif)<=spread/2:
                DMWDPS.append(v)
            elif dif>0:
                DMWDPS.append(DMWDP_med+(v/DMWDP_max)*DMWDP_med*spread/2)
            else:
                DMWDPS.append(DMWDP_med-(DMWDP_min/v)*DMWDP_med*spread/2)

    return DMWDPS


# Нараховані бали цінності приміщень згідно диференціації за поточними цінами та згідно динамічної моделі, обчисленні через мультиплікацію скорингів фактора диференціації поточних цін та динамічної моделі
def DMWPDP_f(stock_df,config):
    DMWPDP = []
    DMWDP = DMWDP_f(stock_df, config)
    for i in range(0,len(stock_df)):
        DMWPDP.append(DMWDP[i]*stock_df['scvdcp'][i])
    return DMWPDP

# Нараховані бали цінності приміщень за базовою гіпотезою та згідно динамічної моделі, обчисленні через мультиплікацію скорингів базової та динамічної моделі
def DMWBHDP_f(stock_df,config):
    DMWBHDP = []
    DMWDP = DMWDP_f(stock_df, config)
    BMRS = BMRS_f(stock_df, config)
    for i in range(0,len(stock_df)):
        DMWBHDP.append(DMWDP[i]*BMRS[i])
    return DMWBHDP

# Умовна вартість приміщень згідно поєднання дифереціацій за ціною наявних приміщень та динамічною моделлю ціноутворення
def DMCWPDP_f(stock_df, config):
    DMCWPDP = []
    DMWPDP = DMWPDP_f(stock_df,config)
    for i in range(0,len(stock_df)):
        DMCWPDP.append(DMWPDP[i]*stock_df['svta'][i])
    return DMCWPDP # 07.07.2021 - исправлено

# Умовна вартість приміщень приміщень згідно поєднання дифереціацій за базової гіпотезою та динамічною моделлю ціноутворення
def DMCWBHDP_f(stock_df, config):
    DMCWBHDP = []
    DMWBHDP = DMWBHDP_f(stock_df,config)
    for i in range(0,len(stock_df)):
        DMCWBHDP.append(DMWBHDP[i]*stock_df['svta'][i])
    return DMCWBHDP

# Частка умовної вартості приміщень згідно поєднання дифереціацій за ціною наявних приміщень та динамічною моделлю ціноутворення
def DMCWSPDP_f(stock_df,config):
    DMCWPDP = DMCWPDP_f(stock_df, config)
    total = sum(DMCWPDP)
    return np.array(DMCWPDP) / total

# Частка умовної вартості приміщень згідно поєднання дифереціацій за базової гіпотезою та динамічною моделлю ціноутворення
def DMCWSBHDP_f(stock_df, config):
    DMCWBHDP = DMCWBHDP_f(stock_df, config)
    total = sum(DMCWBHDP)
    return np.array(DMCWBHDP) / total

# Динамічна вартість приміщень згідно диференціації за цінам ти динамічною моделлю ціноутворення
def DMRCPDP_f (stock_df,plan_df,config):
    return DMCWSPDP_f(stock_df,config)*DMESE_f(stock_df,plan_df,config)

# Динамічна вартість приміщень згідно диференціації за базовою гіпотезою ти динамічною моделлю ціноутворення
def DMRCBHDP_f (stock_df,plan_df,config):
    return DMCWSBHDP_f(stock_df, config)*DMESE_f(stock_df,plan_df,config)

# Динамічна ціна м2 приміщень згідно диференціації за цінам ти динамічною моделлю ціноутворення
def DMDPBHDP_f(stock_df,plan_df,config):
    DMDPBHDP = []
    DMRCBHDP = DMRCBHDP_f(stock_df,plan_df,config)
    for i in range(0,len(stock_df)):
        DMDPBHDP.append(DMRCBHDP[i]/stock_df['svta'][i])
    return DMDPBHDP

# Динамічна ціна м2 приміщень згідно диференціації за базовою гіпотезою ти динамічною моделлю ціноутворення
def DMDPPDP_f(stock_df,plan_df,config):
    DMDPPDP = []
    DMRCPDP = DMRCPDP_f(stock_df,plan_df,config)
    for i in range(0,len(stock_df)):
        DMDPPDP.append(DMRCPDP[i]/stock_df['svta'][i])
    return DMDPPDP

# Динамічна ціна м2 приміщень згідно диференціації що задав користувач
def DMPDPM_f(stock_df,plan_df,config):
    if config['MODE']['additional_diff'] == '1':
        return DMDPBHDP_f(stock_df,plan_df,config)
    else:
        return DMDPPDP_f(stock_df,plan_df,config)
    
# Спотворена динамічна ціна згідго вибраної диференціації розрахована на весь діапазон цін
def DMMPA_f(stock_df,plan_df,config):
    DMMPA = []
    plan_price = MCAPP_f(stock_df,plan_df,config)
    DMPDPM = DMPDPM_f(stock_df,plan_df,config)
    min_price = min([v for v in DMPDPM if v != 0]) #минимальная не нулевая цена
    #print(plan_price - min_price)
    
    if plan_price == min_price:
        #time_name = str(time.time())[-6:]
        #day_name = str(date.today())[-8:]
        print('plan_price = min_price = '+ str(plan_price)) # OPASTNOST DELENIA NA NOL'
        #plan_price += 1 # будет деление на 1 вместо деления на ноль
        #stock_df.to_excel(config['PATH']['out_path']+"output_"+day_name+'_'+time_name+"_stock.xlsx") 
        #plan_df.to_excel(config['PATH']['out_path']+"output_"+day_name+'_'+time_name+"_plan.xlsx")
    for i in range(0,len(stock_df)):
        if plan_price<min_price:
            DMMPA.append(333)
        elif plan_price == min_price: # для последнего дома
            DMMPA.append(DMPDPM[i])
        elif DMPDPM[i] == 0:
            DMMPA.append(0)
        else:
            DMMPA.append(DMPDPM[i] + float(config['DYNAMIC PRICING']['dpmf']) * (plan_price - DMPDPM[i]) * 
                         (1 - (plan_price - DMPDPM[i]) / (plan_price - min_price)))
    return DMMPA

# Спотворена динамічна ціна згідго вибраної диференціації що застосовується у кінцевому розрахунку (спотворюються лише значення нижче MCAPP)
def DMMP_f(stock_df,plan_df,config):
    DMMPA = DMMPA_f(stock_df,plan_df,config)
    DMPDPM = DMPDPM_f(stock_df,plan_df,config)
    comp_price = MCAPP_f(stock_df,plan_df,config)
    DMMP = []
    for i in range(0,len(stock_df)):
        if DMPDPM[i] > comp_price:
            DMMP.append(DMPDPM[i])
        else:
            DMMP.append(DMMPA[i])
    return DMMP

# DMMP з врахуванням природного торгу
def DMMPWB_f(stock_df,plan_df,config):
    return np.array(DMMP_f(stock_df,plan_df,config))*(1-int(config['DYNAMIC PRICING']['dpnb'])/100)

# Публічна (призначена) ціна (maxify price +торг) - считаем новые значения svapp
def DMPMPPB_f(stock_df,plan_df,config):
    DMMPWB = DMMPWB_f(stock_df,plan_df,config)
    DMPMPPB = []
    for i in range(0,len(stock_df)):
        if DMMPWB[i] == 0:
            DMPMPPB.append(0)
        elif stock_df['svapp'][i]>DMMPWB[i]:
            DMPMPPB.append(stock_df['svapp'][i])
        else:
            DMPMPPB.append(DMMPWB[i])
    return DMPMPPB

# Номінальне публічне подорожчання
def DMNPI_f(stock_df,plan_df,config):
    DMPMPPB = DMPMPPB_f(stock_df,plan_df,config)
    DMNPI = []
    for i in range(0,len(stock_df)):
        DMNPI.append(DMPMPPB[i]/stock_df['svapp'][i])
    return DMNPI

# Обмежене номінальне публічне подорожчання - добавлено 06.07.2021
def DMNPIL_f(stock_df, plan_df, config):
    DMNPI = DMNPI_f(stock_df,plan_df,config)
    if max(DMNPI) == 0: # подорожаний нету
        return [0] * len(stock_df)
    elif max(DMNPI) <= float(config['DYNAMIC PRICING']['dpol']): # все подорожания не превышают значения ограничителя
        return DMNPI
    else:
        lim_rate = (float(config['DYNAMIC PRICING']['dpol'])-1)/(max(DMNPI)-1)
        DMNPIL = []
        for i in range(0,len(stock_df)):
            if DMNPI[i] == 0:
                DMNPIL.append(0)
            else:
                DMNPIL.append(1+(DMNPI[i]-1)*lim_rate)
            #else:
            #    DMNPIL.append(1)
        return DMNPIL

# Безумовно Обмежене номінальне публічне подорожчання - добавлено 28.07.2021
def UDMNPIL_f(stock_df, plan_df, config, rate_low = 1.044, rate_hi = 1.1):
    DMNPI = DMNPI_f(stock_df,plan_df,config)
    if max(DMNPI)<=rate_hi:
        return DMNPI
    else:
        lim_rate = (rate_hi-rate_low)/(max(DMNPI)-rate_low)
        UDMNPIL = []
        for v in DMNPI:
            if v<=rate_low:
                UDMNPIL.append(v)
            else:
                UDMNPIL.append(rate_low+lim_rate*(v-rate_low))
        return UDMNPIL

# функция для подсчета подорожания ограниченого/неограниченого в зависимотси от режима вібраного в конфиге - добавлено 09.08.2021
def rip_f(stock_df, plan_df, config):
    if config['MODE']['mode']== 'unconditional':
        rip = UDMNPIL_f(stock_df, plan_df, config)
        print('unconditional mode on')     
    elif config['MODE']['mode']=='default':
        rip = DMNPIL_f(stock_df, plan_df, config)
        print('default mode on')
    elif config['MODE']['mode']=='none':
        rip = DMNPI_f(stock_df, plan_df, config)
        print('limiter is off')
    else:
        print('unknown limiter mode! limiter mode set to default......' )
        rip = DMNPIL_f(stock_df, plan_df, config)
    return rip

# ОБМЕЖЕНА Публічна (призначена) ціна (maxify price +торг) - считаем новые значения svapp, добавлено 06.07.2021 - 28.07.2021 - внесены изменеия чтобы было два режима ограничителя 09.08 -3 ogrnaichitel'a
def DMPMPPBL_f(stock_df,plan_df,config):
    DMPMPPBL = []
    rip = rip_f(stock_df,plan_df,config)
    for i in range(0,len(stock_df)):
        DMPMPPBL.append(stock_df['svapp'][i] * rip[i])
    return DMPMPPBL, rip

# ОБМЕЖЕНА Публічна вартість з торгом - считаем новые значения svfp 
# ПО СУТИ ЭТО ФИНАЛЬНЫЙ ЭТАП ПОДСЧЕТА ЦЕН ПО ДИНАМИЧЕСКОМУ ЦЕНООБРАЗОВАНИЮ
# вернем датафрейм с ценами и стоимостями по айди для помещений
def DMPCBL_f(stock_df,plan_df,config):
    DMPCBL = []
    DMPMPPBL, rip = DMPMPPBL_f(stock_df,plan_df,config)
    for i in range(0,len(stock_df)):
        DMPCBL.append(DMPMPPBL[i]*stock_df['svta'][i])
    #non_zeros = [v for v in DMPMPPBL if not v == 0]
    #zeros = [v for v in DMPMPPBL if v == 0]
    #print(len(zeros))
    #print('min dmppbl: '+str(min(non_zeros)))
    #print('max dmppbl: '+str(max(non_zeros)))
    #print('max-min dmppbl: '+str(max(non_zeros)-min(non_zeros)))
    return pd.DataFrame({'svid':list(stock_df['svid'].values), 'DMPCBL':DMPCBL, 'DMPMPPBL':DMPMPPBL, 'rip':rip})

# Публічна вартість з торгом - считаем новые значения svfp 
# ПО СУТИ ЭТО ФИНАЛЬНЫЙ ЭТАП ПОДСЧЕТА ЦЕН ПО ДИНАМИЧЕСКОМУ ЦЕНООБРАЗОВАНИЮ
# вернем датафрейм с ценами и стоимостями по айди для помещений
def DMPCB_f(stock_df,plan_df,config):
    DMPCB = []
    DMPMPPB = DMPMPPB_f(stock_df,plan_df,config)
    for i in range(0,len(stock_df)):
        DMPCB.append(DMPMPPB[i]*stock_df['svta'][i])
    return pd.DataFrame({'svid':list(stock_df['svid'].values), 'DMPCB':DMPCB, 'DMPMPPB':DMPMPPB})
    
