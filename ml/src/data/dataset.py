from dataclasses import dataclass, field
from typing import List

import pandas as pd

from features.extraction import add_traff_features, statistic_columns

from config.constants import PROJECT_ROOT, PREPROCESSED_DATA_DIR

INDEX_COLUMN = 'abon_id'


@dataclass(frozen=True)
class DataSet:
    testdf: pd.DataFrame = add_traff_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump'))
    traindf: pd.DataFrame = add_traff_features(pd.read_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump'))
    columns: List = traindf.columns.values
