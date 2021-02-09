from boruta import BorutaPy
from lightgbm import LGBMRegressor
import numpy as np
import pandas as pd


# import warnings;
#
# warnings.filterwarnings('ignore')
# https://github.com/scikit-learn-contrib/boruta_py
# https://towardsdatascience.com/boruta-explained-the-way-i-wish-someone-explained-it-to-me-4489d70e154a

def boruta(X, y):
    bor = BorutaPy(estimator=LGBMRegressor(num_boost_round=100), n_estimators='auto', max_iter=10)
    bor.fit(np.array(X), np.array(y))

    return X.columns[bor.support_].to_list(), X.columns[bor.support_weak_].to_list()


def non_empty_columns(df, nans_threshold=6):
    nans_percent_by_column = pd.DataFrame((df.isnull().mean() * 100).apply(lambda x: round(x, 3))) \
        .reset_index().rename(columns={0: 'val', 'index': 'col_name'})

    return nans_percent_by_column[nans_percent_by_column.val < nans_threshold].col_name
