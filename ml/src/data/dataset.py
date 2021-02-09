import pandas as pd

from features.extraction import add_traff_features, statistic_columns

from config.constants import PROJECT_ROOT, PREPROCESSED_DATA_DIR

INDEX_COLUMN = 'abon_id'


class DataSet:
    testdf = add_traff_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump'))
    traindf = add_traff_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump'))
    columns = traindf.columns.values
