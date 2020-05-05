import pandas as pd 
import numpy as np 
import datetime 
from calendar import isleap
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

features = ['GHI', 'DHI', 'DNI', 'precipIntensity', 'precipProbability', 'temperature', 'apparentTemperature', 'dewPoint', 'humidity', 'windSpeed', 'windBearing', 'windGust', 'cloudCover', 'uvIndex', 'visibility', 'day', 'month', 'hour']

def set_nrel_irr_df_dt(df, tz):
    df['date'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    df = df.set_index('date')
    df = df.resample('1H').mean()
    df.index = df.index.tz_localize(tz, nonexistent='NaT', ambiguous='NaT')
    df = df[['GHI','DHI','DNI']]
    return df 

def set_prod_df_dt(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df 

def combine_weather_df(irr_df, prod_df):
    df = irr_df.merge(prod_df, how='inner', left_index=True, right_index=True)

    # It's important to note that the resulting datetime index will be in UTC after the merge 
    return df

def clean_weather_features(df):
    cols_to_drop = ['precipType', 'precipAccumulation', 'pressure', 'ozone', 'summary', 'icon']
    cols_to_drop = [col for col in cols_to_drop if col in list(df.columns)]
    df = df.drop(columns=cols_to_drop)
    return df 

def clean_df(df):
    df = df.dropna(subset=['production'])
    df = df[df['production'] != 0]

    df = clean_weather_features(df)
    return df 

def day_trans(row):
    year = row.name.year 
    day_of_year = row.name.dayofyear
    days_in_year = 366 if isleap(year) else 365
    return np.sin(day_of_year * np.pi / days_in_year)

def add_seasonality(df):
    df['day'] = df.apply(day_trans, axis=1)
    df['month'] = df.apply(lambda row: np.sin(row.name.month * np.pi / 12), axis=1)
    df['hour'] = df.apply(lambda row: np.sin(row.name.hour * np.pi / 24), axis=1)
    return df


def impute_values(df):
    imp = IterativeImputer(missing_values=np.nan, max_iter=10, random_state=0)
    imp.fit(df)
    df_np = imp.transform(df)
    df = pd.DataFrame(df_np, index=df.index, columns=df.columns)
    # display(df)
    return df


def get_final_df(site, prod_df, irr_df): 
    prod_df = set_prod_df_dt(prod_df)
    timezone = site['location']['timeZone']
    irr_df = set_nrel_irr_df_dt(irr_df, timezone)
    df = combine_weather_df(irr_df, prod_df)
    df = clean_df(df)
    df = add_seasonality(df)
    df = impute_values(df)
    df = reorder_columns(df, features + ['production'])
    return df 

def reorder_columns(df, cols):
    df = df[cols]
    return df 