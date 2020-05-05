from sklearn.model_selection import train_test_split

def split(df):
    X, y = train_test_split(df)
    return X, y

    