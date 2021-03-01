from sklearn.metrics import mean_squared_error


def score_rmse(target, predicted):
    return mean_squared_error(target, predicted, squared=False)
