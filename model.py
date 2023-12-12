import numpy as np
import pandas as pd
from sklearn import preprocessing, svm
from sklearn.model_selection import KFold, train_test_split
from sklearn.ensemble import GradientBoostingClassifier
import statsmodels.api as sm


if __name__ == "__main__":

    features = pd.read_csv("feature_table.csv")
    
    X = features.iloc[:, :-1].to_numpy()
    y = features.iloc[:, -1].to_numpy()

    X, X_test, y, y_test = train_test_split(X, y, test_size = 0.2, random_state = 81)

    # standardization
    scaler = preprocessing.StandardScaler().fit(X)
    X = scaler.transform(X)

    svm_scores = []
    gbm_scores = []
    k_fold = KFold(n_splits = 5)
    best_svm_ = None
    best_svm_score = 0
    best_gbm = None
    best_gbm_score = 0
    for train_index, test_index in k_fold.split(X):
        X_train, X_val, y_train, y_val = X[train_index], X[test_index], y[train_index], y[test_index]

        svm_model = svm.SVC()
        svm_model.fit(X_train, y_train)
        svm_score = svm_model.score(X_val, y_val)
        svm_scores.append(svm_score)
        if svm_model.score(X_val, y_val) > best_svm_score:
            best_svm = svm_model
            best_svm_score = svm_score

        gbm_model = GradientBoostingClassifier(max_depth = 2, random_state = 81)
        gbm_model.fit(X_train, y_train)
        gbm_score = gbm_model.score(X_val, y_val)
        gbm_scores.append(gbm_score)
        if gbm_model.score(X_val, y_val) > best_gbm_score:
            best_gbm = gbm_model
            best_gbm_score = gbm_score

    # print(svm_scores)
    # print(gbm_scores)
    print("SVM Validation Accuracy: " + str(np.mean(svm_scores)))
    print("GBM Validation Accuracy: " + str(np.mean(gbm_scores)))

    X_test = scaler.transform(X_test)

    print("SVM Test Accuracy: " + str(best_svm.score(X_test, y_test)))
    print("GBM Test Accuracy: " + str(best_gbm.score(X_test, y_test)))
