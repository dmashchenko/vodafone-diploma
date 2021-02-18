import pickle
from pathlib import Path

from config.constants import OUT_DIR


class TrafficPredictor:
    def __init__(self, model=None, raw_features=[], features_nan_fillers={}):
        self.model = model
        self.raw_features = raw_features

    def predict(self, X):
        X = X[self.raw_features]
        # impute
        # extract features
        return self.model.predict(self.prepare(X))

    @staticmethod
    def prepare(X):
        pass


def build_traffic_predictor():
    return TrafficPredictor()


def publish(predictor: TrafficPredictor):
    Path(OUT_DIR).mkdir(exist_ok=True)
    pickle.dump(predictor, open(OUT_DIR / 'traffic_predictor.pickle', 'wb'))
