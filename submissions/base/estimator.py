
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd
from tqdm import tqdm



class Preprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self  # No fitting necessary

    def transform(self, X):
        features = []
        for i in tqdm(X.index):
            lat,lon=X.loc[i, 'latitude'],X.loc[i, 'longitude']
            precipitation = X.loc[i, 'precipitation']
            air_temp = X.loc[i, 'air_temperature']
            features.append(np.concatenate([[lat], [lon], [precipitation], [air_temp]]))

        df = pd.DataFrame(np.array(features), columns=['lat', 'lon', 'precipitation', 'air_temperature'])

        #normalize lat and lon
        df['lat'] = (df['lat'] - df['lat'].mean()) / df['lat'].std()
        df['lon'] = (df['lon'] - df['lon'].mean()) / df['lon'].std()
        #normalize precipitation and air_temperature
        df['precipitation'] = (df['precipitation'] - df['precipitation'].mean()) / df['precipitation'].std()
        df['air_temperature'] = (df['air_temperature'] - df['air_temperature'].mean()) / df['air_temperature'].std()
        df = df.astype(float)
        
        print("Preprocessing completed.")
        return df
    
    
def get_estimator():
    pipe = make_pipeline(
        Preprocessor(),
        RandomForestClassifier(n_estimators=100)
    )

    return pipe
