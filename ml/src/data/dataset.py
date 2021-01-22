import numpy as np
import pandas as pd
from config.constants import RAW_DATA_DIR

INDEX_COLUMN = 'abon_id'


class DataSet(object):
    def __init__(self):
        self._testdf = None
        self._traindf = None

    def traindf(self):
        if self._traindf is None:
            df1 = self.__load_and_remove_duplicates('train/hash_school_dpi_model_fe.sas7bdat')
            df2 = self.__load_and_remove_duplicates('train/hash_school_dpi_model_traff.sas7bdat')
            self._traindf = self.__merge(df1, df2)
        return self._traindf

    def testdf(self):
        if self._testdf is None:
            df1 = self.__load_and_remove_duplicates('test/hash_school_dpi_model_fe_test.sas7bdat')
            df2 = self.__load_and_remove_duplicates('test/hash_school_dpi_model_traff_test.sas7bdat')
            df3 = self.__load_and_remove_duplicates('test/hash_school_dpi_model_test.sas7bdat')
            self._testdf = self.__merge(self.__merge(df1, df2), df3)
        return self._testdf

    def __load_and_remove_duplicates(self, path):
        result = pd.read_sas(RAW_DATA_DIR / path, index=INDEX_COLUMN)
        result.index = result.index.astype(np.int32)
        self.__remove_duplicates(result)
        return result

    @staticmethod
    def __remove_duplicates(df):
        df.drop(df[df.index.duplicated(keep='first')].index, inplace=True)

    @staticmethod
    def __merge(df1, df2):
        return pd.merge(df1, df2, left_index=True, right_index=True)
