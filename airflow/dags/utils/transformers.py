import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

class CastingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, cols_cat: list=[], cols_num: list=[], cols_date: list=[]):
        assert len(cols_cat) or len(cols_num)
        self.cols_cat = cols_cat
        self.cols_num = cols_num
        self.cols_date = cols_date
    
    def fit(self, X: pd.DataFrame, y=None):
        return self
    
    def transform(self, X: pd.DataFrame):
        X = X.copy()
        for col in self.cols_cat:
            X[col] = pd.Categorical(X[col])
            X[col] = X[col].cat.codes.astype(int)
            
        for col in self.cols_num:
            X[col] = pd.to_numeric(X[col], errors='coerce', downcast='float')
        
        for col in self.cols_date:
            X[col] = pd.to_datetime(X[col], errors='coerce', format='%Y-%m%-%d')
        
        return X
    
class TakeVariables(BaseEstimator, TransformerMixin):
    
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

    