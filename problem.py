import rampwf as rw

import pandas as pd
from pathlib import Path

from sklearn.model_selection import StratifiedShuffleSplit

problem_title = 'Template RAMP kit to create data challenges'

_prediction_label_names = [0, 1]

# A type (class) which will be used to create wrapper objects for y_pred
Predictions = rw.prediction_types.make_multiclass(
    label_names=_prediction_label_names
)

# An object implementing the workflow
workflow = rw.workflows.Estimator()

score_types = [
    
    rw.score_types.Accuracy(name='accuracy', precision=4),
]


def get_cv(X, y):
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2)
    return cv.split(X, y)


def load_data(path='.', file='X_train.csv'):
    path = Path(path) / "data"
    X_df = pd.read_csv(path / file)

    y = X_df['target']
    # map target to integer if not already
    if y.dtype == 'object':
        y = y.map({'high': 1, 'low': 0})
    X_df = X_df.drop(columns=['target'])

    return X_df, y


# READ DATA
def get_train_data(path='.'):
    file = 'X_train.csv'
    return load_data(path, file)


def get_test_data(path='.'):
    file = 'X_test.csv'
    return load_data(path, file)
