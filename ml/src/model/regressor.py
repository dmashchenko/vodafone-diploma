import numpy as np

TRAFF_COLS = ['traff_m1', 'traff_m2', 'traff_m3', 'traff_m4', 'traff_m5']
MONTHS_GAP = 6.0


class LinearRegressor:
    def __init__(self, window=3):
        self.window = window

    def predict(self, df):
        traff_window_df = df[TRAFF_COLS].T.rolling(window=self.window).median()
        traff_window_df.dropna(inplace=True)
        x = np.array(np.arange(0.0, len(traff_window_df.T.columns), 1.0))
        x_mean = x.mean()
        x_residuals = [x - x_mean for x in x]
        residual_x_sum = sum([x ** 2 for x in x_residuals])
        return traff_window_df.T.apply(self.__predict, args=(x, x_mean, x_residuals, residual_x_sum), axis=1)

    @staticmethod
    def __predict(row, x, x_mean, x_residuals, residual_x_sum):
        y = np.array(row)
        y_mean = y.mean()
        y_residuals = [y - y_mean for y in y]
        residual_sum = sum([x * y for x, y in zip(x_residuals, y_residuals)])
        b = residual_sum / residual_x_sum
        a = y_mean - b * x_mean
        result = a + b * (x.size + MONTHS_GAP)
        return result if result > 0 else 0
