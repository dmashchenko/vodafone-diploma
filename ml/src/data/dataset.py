import numpy as np
import pandas as pd

from config.constants import PROJECT_ROOT, PREPROCESSED_DATA_DIR

INDEX_COLUMN = 'abon_id'


class DataSet(object):
    def __init__(self):
        self._testdf = None
        self._traindf = None

    def traindf(self):
        if self._traindf is None:
            self._traindf = pd.read_parquet(PREPROCESSED_DATA_DIR / 'traindf.dump')
        return self._traindf

    def testdf(self):
        if self._testdf is None:
            self._testdf = pd.read_parquet(PREPROCESSED_DATA_DIR / 'testdf.dump')
        return self._testdf
