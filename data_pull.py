import pandas as pd
import numpy as np
import urllib3
import certifi
import json


def purple_air_df():
    http = urllib3.PoolManager(
           cert_reqs='CERT_REQUIRED',
           ca_certs=certifi.where())

    url = "https://www.purpleair.com/json"
    r = http.request('GET', url)
    print('STATUS')
    print(r.status)

    # request and load json file
    pa_data = json.loads(r.data.decode('utf-8'))

    # cast json into df structure
    purple_air_df = pd.json_normalize(pa_data, 'results')
    print('DATAFRAME SHAPE IS...')
    print(purple_air_df.shape)
    print('CLEANING DATA...')

    # fill Stats null values to split Stats column
    purple_air_df['Stats'] = purple_air_df["Stats"].fillna({i: {} for i in purple_air_df.index})

    # split Stats col into individual cols
    purple_air_df[['v', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'pm', 'lastModified',
              'timeSinceModified']] = purple_air_df.Stats.str.split(',', expand=True)
    cols = ['v', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'pm', 'lastModified', 'timeSinceModified']

    for col in cols:
        purple_air_df[col] = purple_air_df[col].str.split(':').str[-1]

    # remove last char on timeSinceModified
    purple_air_df['timeSinceModified'] = purple_air_df['timeSinceModified'].str.replace(r'}', '')

    # rename columns
    purple_air_df.rename(columns={'v':'PM2.5_current',
                                  'v1':'PM2.5_10_min_avg',
                                  'v2':'PM2.5_30_min_avg',
                                  'v3':'PM2.5_1_hour_avg',
                                  'v4':'PM2.5_6_hour_avg',
                                  'v5':'PM2.5_24_hour_avg',
                                  'v6':'PM2.5_1_week_avg',}, inplace=True)

    # change dataframe dtypes
    convert_dict = {'PM2_5Value': float,
                    'humidity': float,
                    'temp_f': float,
                    'pressure': float,
                    'PM2.5_current': float,
                    'PM2.5_10_min_avg': float,
                    'PM2.5_30_min_avg': float,
                    'PM2.5_1_hour_avg': float,
                    'PM2.5_6_hour_avg': float,
                    'PM2.5_24_hour_avg': float,
                    'PM2.5_1_week_avg': float,
                    'pm': float,
                    'lastModified': float,
                    'timeSinceModified': float,
                    }

    purple_air_df = purple_air_df.astype(convert_dict)
    print(purple_air_df.dtypes)

    print('CLEAN DATAFRAME SHAPE IS...')
    print(purple_air_df.shape)
    print(purple_air_df.head())

    return purple_air_df


data = purple_air_df()
print(data.info())

with pd.option_context('display.max_rows', 10, 'display.max_columns', 50, 'display.float_format',
                        '{:0.8}'.format):
    print(data.iloc[0:10,0:33])

pa_missing = data.isnull().sum() / data.isnull().count()
with pd.option_context('display.max_rows', 50, 'display.max_columns', 50, 'display.float_format',
                       '{:0.8}'.format):
    print('Missing Values')
    print(pa_missing.sort_values(ascending=False))

