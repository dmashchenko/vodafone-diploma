import numpy as np
import pandas as pd
import time
from config.constants import RAW_DATA_DIR, PREPROCESSED_DATA_DIR

INDEX_COLUMN = 'abon_id'


def cast_to_float32(df):
    for c in df.columns:
        df[c] = df[c].astype(np.float32)


def load_raw_data_and_make_memory_optimized_dumps():
    start_time = time.time()
    traindf = __load(['train/hash_school_dpi_model_traff.sas7bdat', 'train/hash_school_dpi_model_fe.sas7bdat'])
    testdf = __load(['test/hash_school_dpi_model_traff_test.sas7bdat', 'test/hash_school_dpi_model_fe_test.sas7bdat',
                     'test/hash_school_dpi_model_test.sas7bdat'])

    print("casting to f32...")
    cast_to_float32(traindf)
    cast_to_float32(testdf)
    print("casting completed")

    print("saving to parquet...")
    traindf.to_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump')
    testdf.to_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump')
    print(f"time: {(time.time() - start_time)/60.0: .1f}min")


def __load(paths):
    dfs = []
    for p in paths:
        start_time = time.time()
        print(f"loading: {p}")
        dfs.append(__load_and_remove_duplicates(p))
        print(f"loading is completed {time.time() - start_time: .2f}s")

    print("merging...")
    start_time = time.time()
    result = dfs.pop()
    while len(dfs) > 0:
        result = __merge(result, dfs.pop())
    print(f"merging is completed {time.time() - start_time: .2f}s")

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
