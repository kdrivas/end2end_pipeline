"""
    This file contains transformer classes for scikit learn pipelines.
    The intention is to reuse the code
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
    
class TakeVariables(BaseEstimator, TransformerMixin):
    """
        Take a list of existing variables from the dataframe
    """
    def __init__(self, cols: list):
        assert len(cols) > 0
        self.columns = cols
    
    def fit(self, X: pd.DataFrame, y=None):
        return self
    
    def transform(self, X: pd.DataFrame):
        X = X.copy()
        valid_cols = [col for col in self.columns if col in X.columns]
        X = X[valid_cols]
        return X

class DropNaTransformer(BaseEstimator, TransformerMixin):
    """
        Take a list of existing variables from the dataframe
    """
    def __init__(self, cols: list=[]):
        self.cols = cols
    
    def fit(self, X: pd.DataFrame, y=None):
        return self
    
    def transform(self, X: pd.DataFrame):
        X = X.copy()
        X = X.dropna()
        return X

class FixingFormattedString(BaseEstimator, TransformerMixin):
    """
        Fix financial numbers 
    """
    def __init__(self, cols: list, cols_type: str):
        self.cols = cols
        self.cols_type = cols_type

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def casting_finance(self, x):
        if self.cols_type == 'PIB':
            return int(x.replace('.', ''))
        else: 
            x = x.split('.')
            if x[0].startswith('1'): #es 100+
                if len(x[0]) >2:
                    return float(x[0] + '.' + x[1])
                else:
                    x = x[0]+x[1]
                    return float(x[0:3] + '.' + x[3:])
            else:
                if len(x[0])>2:
                    return float(x[0][0:2] + '.' + x[0][-1])
                else:
                    x = x[0] + x[1]
                    return float(x[0:2] + '.' + x[2:])

    def transform(self, X: pd.DataFrame):
        X = X.copy()
        for col in self.cols:
            if col in X.columns and (X[col].dtypes == 'str' or X[col].dtypes == 'object'):
                X[col] = X[col].apply(lambda x: self.casting_finance(x))
        return X

class RollingTransformer(BaseEstimator, TransformerMixin):
    """
        Perform rolling or shift operations over a set of existing variables
    """
    def __init__(self, cols: list, method: str='mean', window_size: int=3):
        self.cols = cols
        self.window_size = window_size
        self.method = method

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame):
        X = X.copy()

        feats = []
        for col in self.cols:
            if col in X.columns:
                if self.method == 'mean':
                    feat = pd.DataFrame(X[col].rolling(window=self.window_size, min_periods=1).mean())
                elif self.method == 'std':
                    feat = pd.DataFrame(X[col].rolling(window=self.window_size, min_periods=1).std())
                else:
                    raise NotImplementedError
                feat.columns = [f'{col}_rolling{self.window_size}_{self.method}']
                feats.append(feat)

        if len(feats):
            feats = pd.concat(feats, axis=1)
            X = pd.concat([X, feats], axis=1)
            
        return X