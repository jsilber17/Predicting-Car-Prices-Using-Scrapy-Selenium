import numpy as np 
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score 
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from data_cleaning import main as data_tupe 


def split_data(df): 

    """ """ 

    X = df.drop('price', axis=1) 
    y = df.price

    X_train, X_test, y_train, y_test = train_test_split(X, y) 
    
    #X_train = X_train.drop('post_date', axis=1) 
    #X_test = X_test.drop('post_date', axis=1) 

    X_train.odometer = X_train.odometer.fillna(X_train.odometer.mean())
    X_test.odometer = X_test.odometer.fillna(X_test.odometer.mean())

    return X_train, X_test, y_train, y_test 

def standardize_data(X_train, X_test): 

    sc = StandardScaler() 

    X_train = sc.fit_transform(X_train.reset_index(drop=True))
    X_test = sc.fit_transform(X_test.reset_index(drop=True))

    return X_train, X_test

def run_model(cv, scoring, model_type, X_train, X_test, y_train, y_test): 

    """ """ 

    model = model_type

    print(cross_val_score(model, X_train, y_train, cv=cv, scoring=scoring).mean())
    
def main(): 
    
    df = data_tupe()[1]
    X_train, X_test, y_train, y_test = split_data(df)
    X_train, X_test = standardize_data(X_train, X_test) 
    print(run_model(10,'r2', XGBRegressor(), X_train, X_test, y_train, y_test)) 

if __name__ == '__main__': 
    main() 

