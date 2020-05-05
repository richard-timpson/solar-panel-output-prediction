import sys 
sys.path.insert(0, '../')

from data_manipulation import read_data, feature_engineering
import pandas as pd

from cv import split
from training import train_model, evaluate_model

site_md = read_data.read_md()

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
    for site_id, df in dfs.items():
        model, rmse = run_regression(df)
        results[site_id] = rmse 

    results_s = pd.Series(results)
    return results_s
