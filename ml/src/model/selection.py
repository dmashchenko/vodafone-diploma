from sklearn.model_selection import cross_val_score, ShuffleSplit
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.linear_model import LinearRegression, SGDRegressor, Lasso, Ridge, LassoLars, ElasticNet, BayesianRidge, \
    HuberRegressor, RANSACRegressor, TheilSenRegressor, PoissonRegressor, TweedieRegressor, PassiveAggressiveRegressor
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor, GradientBoostingRegressor, ExtraTreesRegressor, \
    HistGradientBoostingRegressor, StackingRegressor, VotingRegressor
from sklearn.svm import SVR, LinearSVR
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import GridSearchCV


def estimate(df, rows=100):
    sample = df.sample(rows, random_state=42)

    X = StandardScaler().fit_transform(sample.drop(columns={'target'}))
    y = sample.target

    for model in [
        LinearRegression,
        SGDRegressor,
        Lasso,
        Ridge,
        LassoLars,
        ElasticNet,
        BayesianRidge,
        HuberRegressor,
        RANSACRegressor,
        # TheilSenRegressor,
        PoissonRegressor,
        TweedieRegressor,
        PassiveAggressiveRegressor,
        DecisionTreeRegressor,
        # RandomForestRegressor, //time consuming
        BaggingRegressor,
        ExtraTreesRegressor,
        GradientBoostingRegressor,
        HistGradientBoostingRegressor,
        KNeighborsRegressor,
        LinearSVR,
        # SVR, //time consuming
        # XGBRegressor,
        LGBMRegressor]:
        _test_and_print_result(model(), model.__name__, X, y)

    _test_and_print_result(CatBoostRegressor(verbose=0), 'CatBoostRegressor', X, y)

    polynomial_regression = Pipeline([('poly', PolynomialFeatures(degree=3)),
                                      ('linear', LinearRegression(fit_intercept=True))])
    _test_and_print_result(polynomial_regression, 'PolynomialRegression', X, y)


def _test_and_print_result(model, label, X, y):
    s = cross_val_score(model, X, y, scoring="neg_root_mean_squared_error", cv=ShuffleSplit(n_splits=5, test_size=.25, random_state=0))
    print(f"{label :30}\t\t RMSE: {s.mean(): .3f}\t\t\t STD: {s.std(): .2f}")


def grid_search_cv(df, model, params, rows=1000):
    sample = df.sample(rows, random_state=42)
    scaler = StandardScaler()

    X = scaler.fit_transform(sample.drop(columns={'target'}))
    y = sample.target

    grid = GridSearchCV(model, params, n_jobs=-1, cv=ShuffleSplit(n_splits=5, test_size=.25, random_state=0), scoring='neg_root_mean_squared_error', verbose=1)
    grid.fit(X, y)

    print(f"Best score: \n{grid.best_score_}")
    print(f"Best params: \n{grid.best_params_}")

    return grid.best_estimator_, scaler
