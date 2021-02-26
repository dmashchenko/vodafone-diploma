from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error


def score_rmse(target, predicted):
    return mean_squared_error(target, predicted, squared=False)


def cross_val_score_rmse(model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    return cross_val_score(model, X_test, y_test, scoring="neg_root_mean_squared_error", cv=5)


def print_cross_val_score_rmse(result):
    print(f"RMSE: {result.mean(): .3f}\t STD: {result.std(): .2f}")
