import pandas as pd
import numpy as np

from features.extraction import add_traff_features, statistic_columns, add_real_lon_lat, add_city_feature, \
    add_station_feature

from config.constants import PROJECT_ROOT, PREPROCESSED_DATA_DIR, RAW_DATA_DIR

INDEX_COLUMN = 'abon_id'


def add_extra_features(df, geodf, station_dict=None):
    if station_dict is None:
        station_dict = {}
    print('adding traffic features ...')
    df = add_traff_features(df)
    print('restoring real lon/lat ...')
    df = add_real_lon_lat(df, geodf)
    print('adding city cluster ...')
    df = add_city_feature(df, geodf[geodf.population >= 100000])
    print('adding station cluster ...')
    return add_station_feature(df, station_dict)


def prepare_geodf(result):
    result.lng = result.lng.astype(np.float32)
    result.lat = result.lat.astype(np.float32)
    result.population = result.population.fillna(result.population.min() / 2.0).astype(np.float32)
    result.capital = result.capital.fillna('minor')

    result = result.set_index('city')
    result.rename(columns={'lng': 'loc_lon', 'lat': 'loc_lat'}, inplace=True)
    result.drop(result[result.index.duplicated(keep='first')].index, inplace=True)

    return result


class DataSet:
    geodf = prepare_geodf(pd.read_csv(RAW_DATA_DIR / 'extra/ua.csv',
                                      usecols=['lng', 'lat', 'city', 'population', 'capital']))
    traindf, station_dict = add_extra_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump'), geodf)
    testdf, _ = add_extra_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump'), geodf, station_dict)
    columns = traindf.columns.values


def get_traffic_by_station_df(df):
    return df.groupby(['loc_lat', 'loc_lon']).agg(
        {'traff_m1': 'sum', 'traff_m2': 'sum', 'traff_m3': 'sum', 'traff_m4': 'sum', 'traff_m5': 'sum',
         'target': 'sum'}).reset_index()


def get_traffic_by_station_for_animation_df(stationdf):
    result = pd.DataFrame()

    for i in range(5, 0, -1):
        col_name = f'traff_m{i}'
        traffdf = stationdf.loc[:, ('loc_lat', 'loc_lon', col_name)]
        traffdf.rename(columns={col_name: 'traffic'}, inplace=True)
        traffdf['month'] = 6 - i
        result = result.append(traffdf, ignore_index=True)

    targetdf = stationdf.loc[:, ('loc_lat', 'loc_lon', 'target')]
    targetdf.rename(columns={'target': 'traffic'}, inplace=True)
    targetdf['month'] = 10

    result = result.append(targetdf, ignore_index=True)

    return result
