import pandas as pd

from features.extraction import add_traff_features, statistic_columns

from config.constants import PROJECT_ROOT, PREPROCESSED_DATA_DIR

INDEX_COLUMN = 'abon_id'


class DataSet:
    testdf = add_traff_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump'))
    traindf = add_traff_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump'))
    columns = traindf.columns.values


def get_traffic_by_station_df(df):
    return df.groupby(['loc_lat', 'loc_lon']).agg(
        {'traff_m1': 'sum', 'traff_m2': 'sum', 'traff_m3': 'sum', 'traff_m4': 'sum', 'traff_m5': 'sum',
         'target': 'sum'}).reset_index()


def get_traffic_by_station_for_animation_df(stationdf):
    result = pd.DataFrame()

    for i in range(1, 6, 1):
        col_name = f'traff_m{i}'
        traffdf = stationdf.loc[:, ('loc_lat', 'loc_lon', col_name)]
        traffdf.rename(columns={col_name: 'traffic'}, inplace=True)
        traffdf['month'] = i
        result = result.append(traffdf, ignore_index=True)

    targetdf = stationdf.loc[:, ('loc_lat', 'loc_lon', 'target')]
    targetdf.rename(columns={'target': 'traffic'}, inplace=True)
    targetdf['month'] = 10

    result = result.append(targetdf, ignore_index=True)

    return result
