import pandas as pd 
import json 

DATA_DIR = '../../data'


def read_weather_irr_df(site):
    site_id = site['id']
    irradiance_id = site['irradiance_site_id']
    production_path = f'{DATA_DIR}/production_data/raw/{site_id}/combination_data/production_weather_combination.csv'
    irradiance_path = f'{DATA_DIR}/irradiance_data/raw/{irradiance_id}/irradiance_data.csv'

    prod_df = pd.read_csv(production_path)
    irr_df = pd.read_csv(irradiance_path)
    return prod_df, irr_df

def read_md():
    with open(f'{DATA_DIR}/production_data/site_metadata.json', 'r') as file:
        s = file.read()
    return json.loads(s)
    
def get_site_by_id(site_id):
    for site in site_md:
        if site['id'] == site_id:
            return site 

site_md = read_md()