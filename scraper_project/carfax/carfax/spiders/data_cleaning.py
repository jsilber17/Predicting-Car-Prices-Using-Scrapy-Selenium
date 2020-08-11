import numpy as np 
import pandas as pd 
import ast
import math
import matplotlib.pyplot as plt 
import seaborn as sns 

def convert_list_of_tupes_to_dict(tup, di):
    di = dict(tup)
    return di


def create_new_cols_from_nested_col(new_col, df, nested_col): 

    val_lst = []

    for col in df[nested_col]: 
        if new_col in col.keys(): 
            try: 
                val_lst.append(col[new_col])
            except KeyError: 
                val_lst.append(np.NaN) 
        else: 
            val_lst.append(np.NaN) 

    return val_lst 


def unnest_initial_dataframe(df): 
    
    ''' ''' 

    # Clean out the date column --> Replacing miscellaneous non alphabetic strings   
    clean_titles = [car.replace('[', "").replace(']', "").replace("'", "") for car in df.title]
    df.title = clean_titles

    # Turn all dates to strings and slice the date to isolate the date 
    post_dates = [str(date)[0:10] for date in df.post_date] 
    df.post_date = pd.to_datetime(df.post_date, infer_datetime_format=True)

    # Drop columns that we do not need from the get-go 
    df.drop(['important_info_fields', 'important_info_values'], axis=1, inplace=True)    

    # Convert the lists of tuples back to strings in important_info column 
    list_of_imp_info = [ast.literal_eval(info) for info in df.important_info]
    df.important_info = list_of_imp_info

    # Convert list of tupes to dictionary inside of the columns  
    dic = {} 

    lst_of_dicts = [convert_list_of_tupes_to_dict(info, dic) for info in df.important_info]
    df.important_info = lst_of_dicts

    list_of_dicts = [df.important_info[key] for key in range(len(df.important_info))]

    unique_keys_in_info = list(set(val for dic in list_of_dicts for val in dic.keys())) 

    # Unnest the DataFrame into new columns 
    for col in unique_keys_in_info: 
        df[col] = create_new_cols_from_nested_col(col, df, 'important_info')

    # Clean unnested DataFrame column names 
    new_cols = [] 
    for col in df.columns: 
        col = col.replace(' ', '_').replace(':', '')
        if col[-1] == '_':
            col = col[0:-1]
            new_cols.append(col)
        else: 
            new_cols.append(col)
    df.columns = new_cols 

    return df 


def fix_columns(df): 

    """ """ 

    # Fixing paint_job 
    lst_of_colors = ['white', 'black', 'silver', 'grey', 'blue', 'red', 'green', 'brown', 'yellow', 'orange', 'purple', 'custom'] 
    paint_job = [] 
    for color in df['paint_color']:
        if color in lst_of_colors:
            paint_job.append(color)
        else:
            paint_job.append(np.NaN)
    df['paint_job'] = paint_job 

    for color in lst_of_colors:
        df.loc[df['fuel'] == color, ['paint_color']] = color
    for color in lst_of_colors:
        df.loc[df['drive'] == color, ['paint_color']] = color
    for color in lst_of_colors:
        df.loc[df['odometer'] == color, ['paint_color']] = color

    # Fixing odometer 
    odometer_in_odometer = []
    for i in df['odometer']: 
        try: 
            odometer_in_odometer.append(int(i))
        except:  
            odometer_in_odometer.append(np.NaN)
    df.odometer = odometer_in_odometer
       
    # Fixing other columns
    acc_vals = [] 

    for col in ['transmission', 'title_status', 'drive', 'cylinders', 'fuel']:
        new_vals = [] 
        if col == 'transmission': 
            acc_vals = ['automatic', 'manual', 'other'] 
        elif col == 'title_status': 
            acc_vals = ['clean', 'other', 'salvage', 'lien', 'missing']
        elif col == 'drive': 
            acc_vals = ['fwd', 'gas', '4wd', 'rwd', 'other', 'electric', 'diesel', 'hybrid']
        elif col == 'cylinders': 
            acc_vals = ['4 cylinders', '6 cylinders', '8 cylinders', '5 cylinders', '10 cylinders', 'other', '3 cylinders', '12 cylinders']
        elif col == 'fuel': 
            acc_vals = ['gas', 'diesel', 'other', 'hybrid', 'electric', 'clean']
        else: 
            print('There is something wrong with the column name') 
            continue 
        
        for val in df[col]: 
            if val in acc_vals: 
                new_vals.append(val)
            else: 
                new_vals.append(np.NaN)

        df[col] = new_vals

    # Fix Title column 
    title = []
    for i in df.title:
        try:
            title.append(i.split(' ')[1])
        except IndexError:
            title.append(i.split(' ')[0])

    title_2 = []
    for i in title:
        try:
            int(i)
            title_2.append('unkown')
        except:
            title_2.append(i.lower().replace('*', ''))

    df_title_2 = pd.DataFrame(title_2)

    df_3 = pd.DataFrame(df_title_2[0].value_counts())

    car_lst = list(df_3[df_3[0]  > 100].index)

    car_lst_final = []

    for i in title_2:
        if i in car_lst:
            if i == 'vw':
                car_lst_final.append('volkswagen')
            elif i == 'mercedes-benz':
                car_lst_final.append('mercedes')
            else:
                car_lst_final.append(i)
        else:
            car_lst_final.append('unknown')

    df['title'] = car_lst_final

    # Fix price column 
    price_lst = [ast.literal_eval(price) for price in df.price]
    df.price = price_lst 

    final_price = []
    for i in df.price:
        if i == []:
            final_price.append('unknown')
        else:
            final_price.append(i[0])

    df.price = final_price
    df = df[df.price != 'unknown']
    
    return df


def impute_data(df): 

    """ """ 

    # Imputing VIN 
    df['VIN'] = df['VIN'].fillna(0) 
    df['has_VIN'] = list(np.where(df['VIN'] == 0, 0, 1))
    df.drop('VIN', axis=1, inplace=True) 

    # Creating region feature based on city 
    cb_region = {
    'northeast': ['newyork', 'boston', 'pittsburgh', 'providence', 'vermont', 'philadelphia', 'rochester', 'buffalo',
                 'newhaven', 'syracuse'],
    'midwest': ['milwaukee', 'grandrapids', 'chicago', 'detroit', 'madison', 'minneapolis', 'stlouis', 'topeka'],
    'south': ['nashville', 'jacksonville', 'atlanta', 'richmond', 'charleston', 'jackson'],
    'west': ['denver', 'sacramento', 'portland', 'spokane', 'sfbay', 'honolulu', 'anchorage', 'albuquerque', 'phoenix',
            'losangeles', 'seattle', 'sandiego', 'boulder', 'santafe']
    }

    cities = []
    for city in df.city:
        if city in cb_region['northeast']:
          cities.append('northeast')
        elif city in cb_region['midwest']:
            cities.append('midwest')
        elif city in cb_region['south']:
            cities.append('south')
        elif city in cb_region['west']:
            cities.append('west')
        else:
            cities.append(city)

    df['city'] = cities

    dummy_region = pd.get_dummies(df['city']).reset_index() 
    region_cols = ['{}_region'.format(col) for col in dummy_region.columns] 
    dummy_region.columns = region_cols 
    df = df.reset_index() 
    df = pd.merge(df, dummy_region, left_on=df.index, right_on=dummy_region.index)
    
    df.drop(['key_0', 'index', 'city', 'index_region'], axis=1, inplace=True) 

    # Creating luxury and foriegn / domestic columns  
    title_unknown = []
    for i in df.title:
        if i == 'unkown':
            title_unknown.append('unknown')
        elif i == '':
            title_unknown.append('unknown')
        else:
            title_unknown.append(i)

    df.title = title_unknown

    d_title_fd = {
    'foreign': ['toyota', 'honda', 'nissan', 'bmw', 'subaru', 'mercedes', 'volkswagen', 'hyundai', 'kia', 'lexus', 
                'mazda', 'audi', 'infiniti', 'acura', 'volvo', 'mini', 'mitsubishi', 'porsche', 'land', 'jaguar', 'isuzu', 'scion'],
    'domestic': ['ford', 'chevrolet', 'dodge', 'jeep', 'chevy', 'gmc', 'ram', 'chrysler', 'cadillac', 'buick', 'pontiac',
                 'mercury', 'saturn', 'freightliner', 'corvette', 'international', 'lincoln'],
    'unknown': ['unknown']
                  
    }

    d_title_lux = {
    'luxury': ['bmw', 'mercedes', 'lexus', 'cadillac', 'audi', 'infiniti', 'acura', 'lincoln', 'porsche', 'land',
               'jaguar', 'corvette'],
    'non_luxury': ['ford', 'toyota', 'chevrolet', 'honda', 'nissan', 'dodge', 'jeep', 'chevy', 'gmc', 'subaru',
                  'volkswagen', 'hyundai', 'ram', 'kia', 'chrysler', 'mazda', 'buick', 'volvo', 'mini',
                   'pontiac', 'mitsubishi', 'international', 'mercury', 'saturn', 'freightliner', 'isuzu', 'scion'],

    'unknown': ['unknown']
    }

    fd = []
    for title in df.title: 
        if title in d_title_fd['foreign']: 
            fd.append('foreign')
        elif title in d_title_fd['domestic']: 
            fd.append('domestic')
        elif title in d_title_fd['unknown']: 
            fd.append('unknown')
        else: 
            fd.append(title)

    lux = []
    for car in df.title: 
        if car in d_title_lux['luxury']: 
            lux.append('luxury')
        elif car in d_title_lux['non_luxury']: 
            lux.append('non_luxury')
        elif car in d_title_lux['unknown']: 
            lux.append('unknown')
        else: 
            print(car)

    df['luxury'] = lux
    df['dom_int'] = fd 

    # Imputing condition column 
    df.condition = df.condition.fillna('unknown')
    new_condition = []
    for condition in df.condition:
        if condition == 'excellent' or condition == 'new':
            new_condition.append('highest')
        elif condition == 'good' or condition == 'like new' or condition == 'fair':
            new_condition.append('middle')
        elif condition == 'salvage':
            new_condition.append('lowest')
        else:
            new_condition.append('unknown')

    df.condition = new_condition

    # Imputing fuel column 
    df.fuel = df.fuel.fillna('unknown')
    new_fuel = []

    for fuel in df.fuel: 
        if fuel == 'gas' or fuel == 'diesel':
            new_fuel.append('non_renewable')
        elif fuel == 'hybrid' or fuel == 'electric' or fuel == 'clean':
            new_fuel.append('renewable')
        else:
            new_fuel.append('unknown')
        
    df.fuel = new_fuel

    # Imputing the rest of the columns 
    df['type'] = df['type'].fillna('sedan') 
    df['paint_color'] = df['paint_color'].fillna('white')
    df['drive'] = df['drive'].fillna('4wd')
    df.cylinders = df.cylinders.fillna('4 cylinders')
    df.transmission = df.transmission.fillna('automatic')
    df.title_status = df.title_status.fillna('clean')
    
    prices = [x.replace('$', '').replace('.', '') for x in df.price]
    df.price = prices
    df = df.drop(df[df.price == ''].index)
    df.price = df.price.astype(int)

    return df

def remove_outliers(df, high_prices, low_prices): 

    """ Remove outliers that have a price above a specified value  """

    df = df[df.price <= high_prices]
    df = df[df.price > low_prices]
    return df 


def dummify_columns(df, list_of_cols): 
    
    """ """ 

    for col in list_of_cols: 
        dummy = pd.get_dummies(df[col]) 
        cols = ['{}_{}'.format(col, val) for val in dummy.columns]
        dummy.columns = cols 

        df = df.merge(dummy, left_on=df.index, right_on=dummy.index) 
        df.drop(['key_0', col], axis=1, inplace=True)

    return df 


def log_y(df): 

    """ """ 
   
    df['price'] = [math.log(p) for p in df['price']]

    return df 
    


def main(): 
    
    df = pd.read_csv('craigslist_csv_combined.csv')

    # Unnest the DataFrame into new columns 
    unnested_dataframe = unnest_initial_dataframe(df)
    
    # Fixes columns used in analysis 
    fixed_columns = fix_columns(unnested_dataframe)

    # Drop unecessary columns 
    dropped_columns = fixed_columns.drop(['delivery_available','size', 'cryptocurrency_ok', 'Unnamed_0', 'items_2', 'important_info', 'items'], axis=1) 

    # Impute the columns 
    imputed = impute_data(dropped_columns)

    # Remove outliers 
    outliers_removed = remove_outliers(imputed, 10000000000000, 0) 

    # Dummify columns 
    dummied = dummify_columns(outliers_removed, ['condition', 'fuel', 'type', 'paint_color', 'transmission', 'title_status', 'drive', 'cylinders', 'luxury', 'dom_int'])
    dummied = dummied.drop(['paint_job', 'title', 'post_date'], axis=1)

    # Log y 
    log_feature = log_y(dummied)
   
    return (imputed, log_feature)
    
if __name__ == '__main__': 
    main() 
