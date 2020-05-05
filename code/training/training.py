import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def train_model(Train):
    model = LinearRegression()
    X_train, y_train = get_X_y(Train)
    model.fit(X_train,y_train)
    return model 

def evaluate_model(model, Test):
    X_test,y_test = get_X_y(Test)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test,y_pred))
    # rmse_norm = rmse / np.max(y_test)

    return rmse

def get_X_y(df):
    cols_to_keep = list(df.columns)
    cols_to_keep.remove('production')
    X = df[cols_to_keep]
    y = df['production']
    return X,y 

