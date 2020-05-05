import pickle
import pandas as pd
import json 

import sys 
sys.path.append('../')

from libraries.weather_api import DarkSkyApi, SolCastApi
from data_manipulation.read_data import get_site_by_id
from data_manipulation.feature_engineering import add_seasonality, clean_weather_features, reorder_columns, features

MODEL_DIR = '../../models'


def load_prod_model(site_id):
    filename = f'{MODEL_DIR}/production/{site_id}/v1.sav'
    model = pickle.load(open(filename, 'rb'))
    return model 

def generate_prod_prediction(site_id, model):
    site = get_site_by_id(site_id)
    lat = site['location']['lat']
    lon = site['location']['long']
    weather_forecast_df = get_weather_forecast_df(lat, lon)
    irr_forecast_df = get_irr_forecast_df(lat, lon)
    feature_df = join_forecast_df(weather_forecast_df, irr_forecast_df)
    preds = model.predict(feature_df)
    preds = pd.Series(preds, index = feature_df.index)
    return preds 
    
def join_forecast_df(weather_forecast_df, irr_forecast_df):
    join_df = weather_forecast_df.merge(irr_forecast_df, how='inner', left_index=True, right_index=True)
    join_df = add_seasonality(join_df)
    join_df = clean_weather_features(join_df)
    feature_df = reorder_columns(join_df, features)
    return feature_df

def get_weather_forecast_df(lat, lon):
    ds_api = DarkSkyApi(True)
    forecast = ds_api.get_forecast(lat, lon)
    data = forecast['hourly']['data']
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['time'], utc=True, unit='s')
    df = df.drop(columns = 'time')
    df = df.set_index('date')
    return df 

def get_irr_forecast_df(lat, lon):
    sc_api = SolCastApi(True)
    forecast = sc_api.get_forecast(lat, lon)
    data = forecast['forecasts']
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['period_end'])
    df = df.set_index('date')
    df = df.rename(columns={'dhi': 'DHI', 'ghi': 'GHI', 'dni': 'DNI'})
    cols_to_drop = [col for col in list(df.columns) if col not in ['DNI', 'DHI', 'GHI']]
    df = df.drop(columns=cols_to_drop)
    return df 
