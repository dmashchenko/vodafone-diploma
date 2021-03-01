from itertools import combinations
from sklearn.feature_selection import mutual_info_regression
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import cross_val_score, ShuffleSplit
from lightgbm import LGBMRegressor
import numpy as np
import pandas as pd
import time


def select_features_by_variance(X, threshold=0.9):
    selector = VarianceThreshold(threshold=(threshold * (1 - threshold))).fit(X)
    return X.columns[selector.get_support(indices=True)]


# https://github.com/scikit-learn-contrib/boruta_py
# https://towardsdatascience.com/boruta-explained-the-way-i-wish-someone-explained-it-to-me-4489d70e154a
def boruta(X, y, iterations=10):
    result_appearance = np.zeros((len(X.columns)))
    result_importance = np.zeros((len(X.columns)))

    for iter_ in range(iterations):
        start_time = time.time()

        np.random.seed(iter_)
        X_shadow = X.apply(np.random.permutation)
        X_shadow.columns = ['shadow_' + feat for feat in X.columns]
        X_boruta = pd.concat([X, X_shadow], axis=1)

        boruta_regressor = LGBMRegressor(random_state=iter_)
        boruta_regressor.fit(X_boruta, y)

        feat_imp_X = boruta_regressor.feature_importances_[:len(X.columns)]
        feat_imp_shadow = boruta_regressor.feature_importances_[len(X.columns):]

        result_appearance += (feat_imp_X > feat_imp_shadow.max())

        mx = feat_imp_X.max()
        mn = feat_imp_X.min()
        result_importance += np.array([(x - mn) / (mx - mn) for x in feat_imp_X])

        print(f"{iter_ + 1}. iteration is finished... {time.time() - start_time: .1f}s")

    return pd.Series(index=X.columns, data=result_appearance), pd.Series(index=X.columns, data=result_importance)


def grid_search(traindf, base_features, features_to_select, max_count_to_add=3):
    result = []
    regressor = LGBMRegressor()
    for i in range(1, max_count_to_add + 1):
        start_time = time.time()

        result_features = []
        result_score = []
        for f in list(combinations(features_to_select, i)):
            features = base_features + list(f)
            score = cross_val_score(regressor, traindf[features], traindf.target,
                                    scoring="neg_root_mean_squared_error",
                                    cv=ShuffleSplit(n_splits=3, test_size=.33, random_state=0))
            result_features.append(f)
            result_score.append(score.mean())

        result.append(pd.Series(index=result_features, data=result_score))
        print(f"{i}. iteration is finished... {time.time() - start_time: .1f}s")

    return result


def mutual_info(X, y):
    mi_scores = mutual_info_regression(X, y)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    return mi_scores.sort_values(ascending=False)


def non_empty_columns(df, nans_threshold=6):
    nans_percent_by_column = pd.DataFrame((df.isnull().mean() * 100).apply(lambda x: round(x, 3))) \
        .reset_index().rename(columns={0: 'val', 'index': 'col_name'})

    return nans_percent_by_column[nans_percent_by_column.val < nans_threshold].col_name


def correlation(df, target, threshold=0.3):
    corr_target = df.drop(target, axis=1).apply(lambda x: x.corr(df[target]))
    columns = corr_target[abs(corr_target) > threshold]
    return columns.sort_values()
