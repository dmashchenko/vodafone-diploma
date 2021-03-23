from sklearn.impute import SimpleImputer
import numpy as np


class Imputer:
    def __init__(self, X):
        self.X = X

    def fit_transform(self):
        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        return imputer.fit_transform(self.X)
