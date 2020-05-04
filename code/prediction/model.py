import pickle
import pandas as pd
import json 
from weather_api import DarkSkyApi, SolCastApi

MODEL_DIR = '../../models'

with open('../../data/production_data/site_metadata.json', 'r') as file:
    s = file.read()

site_md = json.loads(s)

def get_site_by_id(site_id):
    for site in site_md:
        if site['id'] == site_id:
            return site 


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
    

def get_weather_forecast_df(lat, lon):
    ds_api = DarkSkyApi()
    forecast = ds_api.get_forecast(lat, lon)
    data = forecast['hourly']['data']
    df = pd.DataFrame(data)
    return df 

def get_irr_forecast_df(lat, lon):
    sc_api = SolCastApi()
    forecast = sc_api.get_forecast(lat, lon)
    data = forecast['forecasts']
    df = pd.DataFrame(data)
    return df 
