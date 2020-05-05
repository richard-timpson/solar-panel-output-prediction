import pandas as pd
import os 
import pickle

import sys 
sys.path.insert(0, '../')

from data_manipulation import read_data, feature_engineering
from cv import split
from training import train_model, evaluate_model

site_md = read_data.read_md()
MODEL_DIR = '../../models'


def read_site_data(site):
    prod_df, irr_df = read_data.read_weather_irr_df(site)
    df = feature_engineering.get_final_df(site, prod_df, irr_df)
    return df 

def read_all_sites():
    dfs = {}
    for site in site_md:
        try: 
            df = read_site_data(site)
            dfs[site['id']] = df
        except FileNotFoundError:
            print(f'Couldn\'t train for system {site["id"]}, no irradiance data')
        
    return dfs

def run_regression(df):
    Train, Test = split(df)

    model = train_model(Train)
    rmse = evaluate_model(model, Test)

    return model, rmse 

def run_regression_all():
    dfs = read_all_sites()
    results = {}
    models = {}
    for site_id, df in dfs.items():
        model, rmse = run_regression(df)
        results[site_id] = rmse 
        models[site_id] = model 

    results_s = pd.Series(results)
    return results_s, models


def save_model(site_id, model):
    d = f'{MODEL_DIR}/production/{site_id}'

    if not os.path.exists(d):
        os.mkdir(d)

    filename = f'{d}/v1.sav'
    pickle.dump(model, open(filename, 'wb'))

def save_models(models):
    for site_id, model in models.items():
        save_model(site_id, model )
