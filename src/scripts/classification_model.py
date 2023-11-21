import numpy as np
import pandas as pd
import datetime
import pandasql as ps
import statsmodels.api as sm
import read_write as io
from sklearn.model_selection import train_test_split
from sklearn import metrics

def generaModelo(X_train, y_train):
    '''Backward propagation logistic model'''
    listVarNoPV = []
    model = sm.Logit(y_train, X_train)
    results = model.fit()
    pValues = results.pvalues.sort_values(ascending = False)[:1]
    varParam = results.params.sort_values(ascending = False)[:1]
    print(pValues[0])
    print(varParam.index[0])
    while (pValues[0] > 0.05) | ( varParam[0] > 0 ):
        if pValues[0] > 0.05:
            listVarNoPV.append(pValues.index[0])
        elif varParam[0] > 0:
            listVarNoPV.append(varParam.index[0])
        else:
            print("Error")
        print(listVarNoPV)
        model = sm.Logit(y_train, X_train.loc[:, sorted(list(set(X_train.columns) - set(listVarNoPV)))])
        results = model.fit()
        pValues = results.pvalues.sort_values(ascending = False)[:1]
        varParam = results.params.sort_values(ascending = False)[:1]
        print(pValues[0])
        print(varParam.index[0])
    return listVarNoPV, results

def split_train_test(df ,predict_vars, test_size=0.3, target = 'target'):
    '''Split the data in train and test'''
    X = df[predict_vars]
    y = df[target].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    return X_train, X_test, y_train, y_test

def pred_proba(results, listVarNoPV, X_train, X_test):
    '''predict data'''
    prob_threshold = 0.5
    train_pred_proba = results.predict(X_train.loc[:, sorted(list(set(X_train.columns) - set(listVarNoPV)))])
    test_pred_proba = results.predict(X_test.loc[:, sorted(list(set(X_train.columns) - set(listVarNoPV)))])

    train_pred=(train_pred_proba > prob_threshold).apply(int)
    test_pred=(test_pred_proba > prob_threshold).apply(int)
    return train_pred, test_pred, train_pred_proba, test_pred_proba

def metrics_model(y_train, y_test, train_pred, test_pred, train_pred_proba, test_pred_proba):
    # Metrics
    print("\nAUC Model")
    print("AUC Train:", metrics.roc_auc_score(y_train,train_pred_proba))
    print("AUC Test:", metrics.roc_auc_score(y_test,test_pred_proba))
    print("\nGINI Model")
    print("GINI Train:", 2 * metrics.roc_auc_score(y_train,train_pred_proba) - 1)
    print("GINI Test:", 2 * metrics.roc_auc_score(y_test,test_pred_proba) - 1)
    print("\nAccuracy | Precision ")
    print("Accuracy Train:", metrics.accuracy_score(y_train,train_pred))
    print("Accuracy Test:", metrics.accuracy_score(y_test,test_pred))
    print("\nRecall")
    print("Recall Train:", metrics.recall_score(y_train,train_pred))
    print("Recall Test:", metrics.recall_score(y_test,test_pred))
    print("\nPrecision")
    print("Precision Train:", metrics.precision_score(y_train,train_pred))
    print("Precision Test:", metrics.precision_score(y_test,test_pred))
    print("\nF1")
    print("F1 Train:", metrics.f1_score(y_train,train_pred))
    print("F1 Test:", metrics.f1_score(y_test,test_pred))

def main():
    df = io.read_data(io.Filenames.data_transformed_woe)
    # Columns transformed
    predict_vars = [c for c in df.columns if c.endswith('_WOE_OB')]
    predict_vars = set(predict_vars) - {'RS_E_OilPress_PC1_WOE_OB','RS_E_WatTemp_PC1_WOE_OB',}
    # df filtered for model
    df_model = df.loc[(df['period']>='2023-04-01') & (df['target'].isin([0,1])),predict_vars+['target']]
    # split data
    X_train, X_test, y_train, y_test = split_train_test( df_model, predict_vars, test_size=0.3, target = 'target')
    # add constant
    X_train=sm.add_constant(X_train)
    X_test=sm.add_constant(X_test)
    #model
    listVarNoPV, results = generaModelo(X_train, y_train)
    print(results)
    #train_pred, test_pred, train_pred_proba, test_pred_proba  = pred_proba(results, listVarNoPV, X_train, X_test)
    #metrics_model(y_train, y_test, train_pred, test_pred, train_pred_proba, test_pred_proba)
    return

if __name__ == "__main__":
    main()