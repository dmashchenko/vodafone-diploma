import numpy as np
import pandas as pd
from config.constants import RAW_DATA_DIR, PREPROCESSED_DATA_DIR

INDEX_COLUMN = 'abon_id'


def cast_to_float32(df):
    for c in df.columns:
        df[c] = df[c].astype(np.float32)


def load_raw_data_and_make_memory_optimized_dumps():
    traindf = __load(['train/hash_school_dpi_model_traff.sas7bdat', 'train/hash_school_dpi_model_fe.sas7bdat'])
    testdf = __load(['test/hash_school_dpi_model_traff_test.sas7bdat', 'test/hash_school_dpi_model_fe_test.sas7bdat',
                     'test/hash_school_dpi_model_test.sas7bdat'])

    cast_to_float32(traindf)
    cast_to_float32(testdf)

    traindf.to_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump')
    testdf.to_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump')


def __load(paths):
    dfs = []
    for p in paths:
        dfs.append(__load_and_remove_duplicates(p))

    result = dfs.pop()
    while len(dfs) > 0:
        result = __merge(result, dfs.pop())

    return result


def __load_and_remove_duplicates(path):
    result = pd.read_sas(RAW_DATA_DIR / path, index=INDEX_COLUMN)
    result.index = result.index.astype(np.int32)
    __remove_duplicates(result)
    return result


def __remove_duplicates(df):
    df.drop(df[df.index.duplicated(keep='first')].index, inplace=True)


def __merge(df1, df2):
    return pd.merge(df1, df2, left_index=True, right_index=True)
