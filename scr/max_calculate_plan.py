import pandas as pd
import numpy as np
# запишем функцию которая будет считать процент распроданности по прошествии М месяцев с начала старта продаж
# распроданность возвращаем как словарь содержащий 4 значения - по одному для каждого типа помещений
def sold_out_percentage (coefs_df, input_df, M):
    sold_out_dict = {'appartments':0,'offices':0,'parking_spaces':0, 'commerce':0}
    project_class = str(int(input_df.loc[input_df['field name']=='project_class']['value'])) # класс проекта, нужен чтобы выбрать нужные коэф
    coef_a = float(coefs_df.loc[coefs_df['field name']=='coef_a_'+project_class]['value']) # коеф a данного проекта
    coef_b = float(coefs_df.loc[coefs_df['field name']=='coef_b_'+project_class]['value']) # коеф b данного проекта
    dp_coef = -0.4 * np.log(float(input_df.loc[input_df['field name']=='hansel_amount']['value'])*10) + float(coefs_df.loc[coefs_df['field name']=='down_payment_coef']['value']) # третий коеф размер которого зависит от размера ПВ
    
    # чтобы получить для каждого из типов помещений процент распроданости найдем проценты завершенности срока строительства
    appartment_readiness = 100 * (M - int(coefs_df.loc[coefs_df['field name']=='appartments_delay']['value']))/int(input_df.loc[input_df['field name']=='duration_of_constr']['value'])
    parking_spaces_readiness = 100 * (M - int(coefs_df.loc[coefs_df['field name']=='parking_spaces_delay']['value']))/int(input_df.loc[input_df['field name']=='duration_of_constr']['value'])
    if appartment_readiness <= 0: 
        sold_out_dict['appartments'] = 0
    else:
        apparments_sold_out = coef_a * dp_coef * (appartment_readiness+1) ** coef_b
        if apparments_sold_out > 1:
            sold_out_dict['appartments'] = 1
        else:
            sold_out_dict['appartments'] = apparments_sold_out
    if parking_spaces_readiness <= 0:
        sold_out_dict['parking_spaces'] = 0
    else:
        parking_spaces_sold_out = coef_a * dp_coef * (parking_spaces_readiness+1) ** coef_b
        if parking_spaces_sold_out > 1:
            sold_out_dict['parking_spaces'] = 1
        else:
            sold_out_dict['parking_spaces'] = parking_spaces_sold_out
    
    # для офисов и коммерции распроданность считаем линейно
    office_sold_out = (M - int(coefs_df.loc[coefs_df['field name']=='offices_delay']['value']))/int(input_df.loc[input_df['field name']=='duration_of_constr']['value'])
    commerce_sold_out = (M - int(coefs_df.loc[coefs_df['field name']=='commerce_delay']['value']))/int(input_df.loc[input_df['field name']=='duration_of_constr']['value'])
    if office_sold_out <= 0:
        sold_out_dict['offices'] = 0
    elif office_sold_out >= 1:
        sold_out_dict['offices'] = 1
    else:
        sold_out_dict['offices'] = office_sold_out
    if commerce_sold_out <= 0:
        sold_out_dict['commerce'] = 0
    elif commerce_sold_out >= 1:
        sold_out_dict['commerce'] = 1
    else:
        sold_out_dict['commerce'] = commerce_sold_out
    return sold_out_dict

# функция возвращает процент распроданости на М-том месяце с начала продаж
def sold_out_percentage_delta (coefs_df, input_df, M):
    sold_out_dict = {}
    sold_out_dict['appartments'] = sold_out_percentage (coefs_df, input_df, M)['appartments'] - sold_out_percentage (coefs_df, input_df, M-1)['appartments']  
    sold_out_dict['offices'] = sold_out_percentage (coefs_df, input_df, M)['offices'] - sold_out_percentage (coefs_df, input_df, M-1)['offices']  
    sold_out_dict['parking_spaces'] = sold_out_percentage (coefs_df, input_df, M)['parking_spaces'] - sold_out_percentage (coefs_df, input_df, M-1)['parking_spaces']  
    sold_out_dict['commerce'] = sold_out_percentage (coefs_df, input_df, M)['commerce'] - sold_out_percentage (coefs_df, input_df, M-1)['commerce']  
    return sold_out_dict

# запишем функцию которая будет считать распроданность в метрах кв. по прошествии М месяцев с начала старта продаж
# распроданность возвращаем как словарь содержащий 4 значения - по одному для каждого типа помещений
def sold_out_rate(coefs_df, input_df, M):
    season = str((int(input_df.loc[input_df['field name']=='start_month']['value']) + M-1)%12)
    season_coef = float(coefs_df.loc[coefs_df['field name']=='season_coef_'+season]['value'])
    sold_out_dict = {}
    percentage_delta = sold_out_percentage_delta (coefs_df, input_df, M)
    #print(season_coef)
    #print(percentage_delta['appartments'])
    sold_out_dict['appartments'] = percentage_delta['appartments'] * season_coef * float(input_df.loc[input_df['field name']=='appartments_area']['value'])
    sold_out_dict['offices'] = percentage_delta['offices'] * season_coef * float(input_df.loc[input_df['field name']=='offices_area']['value'])
    sold_out_dict['parking_spaces'] = percentage_delta['parking_spaces'] * season_coef * float(input_df.loc[input_df['field name']=='parking_spaces_area']['value'])
    sold_out_dict['commerce'] = percentage_delta['commerce'] * season_coef * float(input_df.loc[input_df['field name']=='commerce_area']['value'])
    return sold_out_dict

# функця которая возвращает период реализации для конкретного типа помещений
def implementation_period(coefs_df, input_df, room_type):
    i = 0
    while not sold_out_percentage (coefs_df, input_df, i)[room_type] == 1:
        i+=1
    return i

# функция которая возвращает список распроданостей площадей для заданого типа помещений
def get_sold_out_rate_list (coefs_df, input_df, room_type):
    period = implementation_period(coefs_df, input_df, room_type)
    sold_out_rate_list = []
    for i in range(0,period):
        sold_out_rate_list.append(sold_out_rate(coefs_df, input_df, i)[room_type])
    residual = float(input_df.loc[input_df['field name']==room_type+'_area']['value']) - sum(sold_out_rate_list)
    number_of_non_zero_soldouts = len([v for v in sold_out_rate_list if v > 0])
    for i in range(0,period):
        if not sold_out_rate_list[i] == 0:
            sold_out_rate_list[i] += residual/number_of_non_zero_soldouts
    return sold_out_rate_list  

# функция которая возвращает список количества купленых помещений заданого типа
def get_amount_of_sold_list(coefs_df, input_df, room_type):
    sold_out_rate_list = get_sold_out_rate_list (coefs_df, input_df, room_type) 
    mean_area = float(input_df.loc[input_df['field name']==room_type+'_area']['value'])/float(input_df.loc[input_df['field name']==room_type+'_amount']['value'])
    amount_list = []
    for v in sold_out_rate_list:
        amount_list.append(v/mean_area)
    return amount_list

# функция которая возвращает список распроданостей площадей в процентах для заданого типа помещений
def get_sold_out_percentage_list (coefs_df, input_df, room_type):
    period = implementation_period(coefs_df, input_df, room_type)
    sold_out_percentage_list = []
    for i in range(0,period):
        sold_out_percentage_list.append(sold_out_percentage(coefs_df, input_df, i)[room_type])
    return sold_out_percentage_list  

# функция возвращает накопленную распроданность
def get_sold_out_sum_list(sold_out_rate_list):
    sold_out_sum_list = []
    current_sum = 0
    for v in sold_out_rate_list:
        current_sum += v
        sold_out_sum_list.append(current_sum)
    return sold_out_sum_list

# функция для расчета цен для заданого типа помещений
def get_price_list(coefs_df, input_df, room_type):
    s_o_r = get_sold_out_rate_list (coefs_df, input_df, room_type)
    total_area = float(input_df.loc[input_df['field name']==room_type+'_area']['value'])
    basic_price = float(input_df.loc[input_df['field name']==room_type+'_basic_price']['value'])
    # формула расчета заданой доходности (2 вида, 1 для квартир и паркомест второй для коммерции и офисов) на основании нормы доходности и длительности строительства
    if room_type in ['appartments', 'parking_spaces']:
        profitability_coef = float(input_df.loc[input_df['field name']=='rate_of_return']['value'])/12*float(input_df.loc[input_df['field name']=='duration_of_constr']['value'])*1.4
    elif room_type in ['offices', 'commerce']:
        profitability_coef = float(input_df.loc[input_df['field name']=='rate_of_return']['value'])/12*float(input_df.loc[input_df['field name']=='duration_of_constr']['value'])
    price_list = []
    current_coef = 1
    current_percentage_of_sales = 0
    for i in range(0,len(s_o_r)):
        current_percentage_of_sales = s_o_r[i]/total_area
        # в зависимости от режима доходности коеф для модификации цен считаются одним из трех способов:
        if int(input_df.loc[input_df['field name']=='profitability_mode']['value']) == 0:
            current_coef = current_coef + current_percentage_of_sales * profitability_coef
        elif int(input_df.loc[input_df['field name']=='profitability_mode']['value']) == 1:
            c = {'appartments':1.0, 'offices':0.95, 'parking_spaces':0.95,  'commerce':0.95}[room_type]
            d = {'appartments':0.10, 'offices':0.05, 'parking_spaces':0.05,  'commerce':0.03}[room_type]
            current_coef = c*i**d
        else:
            e = {'appartments':1.0, 'offices':0.95, 'parking_spaces':0.95,  'commerce':0.95}[room_type]
            f = 0.0099
            current_coef = e*np.exp(f*i)
            
     
        price_list.append(basic_price * current_coef)
    return price_list

# функция для расчета сумм подписаных договоров для заданого типа помещений        
def get_contracts_amount_list(coefs_df, input_df, room_type):
    price_list = get_price_list(coefs_df, input_df, room_type)
    s_o_r = get_sold_out_rate_list (coefs_df, input_df, room_type)[1:]
    contracts_amount_list = []
    for i in range(0,len(s_o_r)):
        contracts_amount_list.append(price_list[i]*s_o_r[i])
    return contracts_amount_list

# функция для расчета списка сумм поступлений для заданого типа помещений
def get_amount_of_receipts_list(coefs_df, input_df, room_type):
    # процент поступающих сразу финансов
    payment_percent = (1 - float(input_df.loc[input_df['field name']=='hansel_amount']['value']))*float(input_df.loc[input_df['field name']=='hansel_amount']['value'])+float(input_df.loc[input_df['field name']=='hansel_amount']['value'])
    contracts_amount_list = get_contracts_amount_list(coefs_df, input_df, room_type)
    full_payments = []
    installment_residuals = []
    for i in range(0,len(contracts_amount_list)):
        full_payments.append(contracts_amount_list[i]*payment_percent)
        installment_residuals.append(contracts_amount_list[i]*(1-payment_percent))
    current_installment = int(input_df.loc[input_df['field name']=='duration_of_install_max']['value'])
    min_installment = int(input_df.loc[input_df['field name']=='duration_of_install_min']['value'])
    amount_of_receipts_list = full_payments
    for i,v in enumerate(installment_residuals):
        for j in range(1,current_installment+1):
            if len(amount_of_receipts_list) <= i+j:
                amount_of_receipts_list.append(v/current_installment)
            else:
                amount_of_receipts_list[i+j]+=v/current_installment
        if current_installment > min_installment:
            current_installment-=1   
    return amount_of_receipts_list

def generate_df_from_list(project_name, test_list, qa_list):
    res=pd.DataFrame(columns=['field name','value'])
    res = pd.concat([res,pd.DataFrame({'field name':'start_year','value':test_list[2]}, index =[0])])
    res = pd.concat([res,pd.DataFrame({'field name':'start_month','value':test_list[3]}, index =[1])])
    res = pd.concat([res,pd.DataFrame({'field name':'duration_of_constr','value':test_list[4]}, index =[2])])
    res = pd.concat([res,pd.DataFrame({'field name':'duration_of_install_min','value':test_list[5]}, index =[3])])
    res = pd.concat([res,pd.DataFrame({'field name':'duration_of_install_max','value':test_list[6]}, index =[4])])
    res = pd.concat([res,pd.DataFrame({'field name':'project_class','value':{'эконом':1,'комфорт':2,'бизнес':3,'элит':4}[test_list[0]]}, index =[5])])
    res = pd.concat([res,pd.DataFrame({'field name':'project_name','value':project_name}, index =[6])])
    res = pd.concat([res,pd.DataFrame({'field name':'profitability_mode','value':{'Константа':0, 'Рост доходности во времени':1, 'Снижение доходности во времени':2}[test_list[9]]}, index =[7])])
    res = pd.concat([res,pd.DataFrame({'field name':'hansel_amount','value':test_list[7]}, index =[8])])
    res = pd.concat([res,pd.DataFrame({'field name':'rate_of_return','value':test_list[8]}, index =[9])])
    res = pd.concat([res,pd.DataFrame({'field name':'appartments_amount','value':qa_list[0]}, index =[10])])
    res = pd.concat([res,pd.DataFrame({'field name':'appartments_area','value':qa_list[1]}, index =[11])])
    res = pd.concat([res,pd.DataFrame({'field name':'appartments_basic_price','value':test_list[1]}, index =[11])])
    i= 12
    for v in ['offices_amount','offices_area','offices_basic_price','parking_spaces_amount','parking_spaces_area','parking_spaces_basic_price','commerce_amount','commerce_area','commerce_basic_price']:
        res= pd.concat([res, pd.DataFrame({'field name':v,'value':0},index = [i])])
        i+=1
    return res

def generate_plan_table(building_id, input_pars_list, input_qa_list, coefs_df):
    input_df = generate_df_from_list(building_id, input_pars_list, input_qa_list)
    plan = {}
    duration = implementation_period(coefs_df, input_df, 'appartments')-1
    plan['pvh'] = [building_id]*duration
    plan['pvp'] = [building_id]*duration
    plan['pva'] = get_sold_out_rate_list (coefs_df, input_df, 'appartments')[1:]
    plan['pvca'] = get_contracts_amount_list(coefs_df, input_df, 'appartments')
    current_year = int(input_df.loc[input_df['field name']=='start_year']['value'])
    current_month = int(input_df.loc[input_df['field name']=='start_month']['value'])
    year_list = []
    month_list = []
    for i in range(0,duration):
        month_list.append(current_month)
        year_list.append(current_year)
        current_month+=1
        if current_month == 12:
            current_year+=1
            current_month=0
    plan['year'] = year_list
    plan['month'] = month_list
    
    return pd.DataFrame(plan).sort_values(by=['year','month'])    