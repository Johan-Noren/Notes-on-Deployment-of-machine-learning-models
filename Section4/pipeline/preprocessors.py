import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


# Add binary variable to indicate missing values
class MissingIndicator(BaseEstimator, TransformerMixin):

    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables

    def fit(self, X, y=None):
        # to accommodate sklearn pipeline functionality
        return self


    def transform(self, X):
        # add indicator
        X = X.copy()
        
        for feature in self.variables:
            X[feature+'_na'] = np.where(X[feature].isnull(),1,0)
            
        return X

# categorical missing value imputer
class CategoricalImputer(BaseEstimator, TransformerMixin):

    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables

    def fit(self, X, y=None):
        # we need the fit statement to accommodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        
        for feature in self.variables:
            X[feature] = X[feature].fillna('Missing')
        
        return X
    


# Numerical missing value imputer
class NumericalImputer(BaseEstimator, TransformerMixin):

    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables
    
    def fit(self, X, y=None):
        # persist mode in a dictionary
        self.imputer_dict_ = {}
        
        for feature in self.variables:
            self.imputer_dict_[feature] = X[feature].mode()[0]
            
        return self

    def transform(self, X):

        X = X.copy()
        
        for feature in self.variables:
            X[feature].fillna(self.imputer_dict_[feature], inplace=True)
        
        return X


# Extract first letter from string variable
class ExtractFirstLetter(BaseEstimator, TransformerMixin):

    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables
    
    def fit(self, X, y=None):
        # we need this step to fit the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        
        for variable in self.variables:
            X[variable] = X[variable].str[0]
        
        return X
        
    
# frequent label categorical encoder
class RareLabelCategoricalEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, tol=0.05, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables
            
    def fit(self, X, y=None):

        # persist frequent labels in dictionary
        self.encoder_dict_ = {}
        
        def find_frequent_labels(df, var, rare_perc):
            tmp = df.groupby(var)[var].count() / len(df)
            return tmp[tmp > rare_perc].index
        
        for feature in self.variables:
        
            frequent_ls = find_frequent_labels(X, feature, 0.05)
            self.encoder_dict_[feature] = frequent_ls
        
        return self
        
    def transform(self, X):
        X = X.copy()
        
        for feature in self.variables:
            X[feature] = np.where(X[feature].isin(self.encoder_dict_[feature]), X[feature], 'Rare')
        
        return X

# string to numbers categorical encoder
class CategoricalEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables
            
            
    def fit(self, X, y=None):

        # HINT: persist the dummy variables found in train set
        self.dummies = pd.get_dummies(X[self.variables], drop_first=True).columns
        
        return self

    def transform(self, X):
        # encode labels
        X = X.copy()
        # get dummies
        
        for feature in self.variables:
        
            X = pd.concat([X.drop(feature, axis=1), pd.get_dummies(X[feature], prefix=feature, drop_first=True)], axis=1)
       
        # drop original variables
        # done
        
        
        # add missing dummies if any
        for feature in self.dummies:
            if feature not in X.columns:
                X[feature] = 0
                
        return X
