# coding=utf-8

import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn import cross_validation

def pre_process_data():
    print("begin to read data")
    train_data = pd.read_excel('train.xlsx')
    x_test = pd.read_excel('train.xlsx')

    # 去掉空行
    print("raw_data:" + str(train_data.shape))
    nan_data_value = remove_nan_data(train_data)

    train_data.drop(nan_data_value, axis=1, inplace=True)
    print("remove nan data:" + str(train_data.shape))
    float_data = remove_no_float(train_data)
    # train_data = remove_date(train_data)
    train_data = train_data[float_data]
    print(float_data)
    print(train_data.shape)
    train_data = remove_waste_col(train_data)
    print(train_data.shape)
    y_train = train_data['Y']
    train_data.drop(['Y'], axis=1, inplace=True)
    x_train = normalize_data(train_data)
    x_train.fillna(x_train.mean())
    corr_df = cal_corrcoef(x_train, y_train)
    corr02 = corr_df[corr_df.corr_value >= 0.2]
    corr02_col = corr02['col'].values.tolist()
    x_train = x_train[corr02_col]
    x_test = x_test[corr02_col]
    x_test = normalize_data(x_test)
    x_test.fillna(x_test.mean())
    print("Finish preprocess")
    print(x_train.shape, y_train.shape)
    return x_train.values, y_train.values, x_test.values


def remove_nan_data(data):
    nan_data = data.isnull().sum(axis=0).reset_index()
    nan_data.columns = ['col', 'nan_count']
    nan_data = nan_data.sort_values(by='nan_count')
    nan_data_value = nan_data[nan_data.nan_count > 200].col.values
    print("nan_data_value:" + str(nan_data_value))
    return nan_data_value


#  删除非数字行
def remove_no_float(data):
    data_type = data.dtypes.reset_index()
    data_type.columns = ['col', 'dtype']
    return data_type[data_type.dtype != 'object'].col.values


# 计算协方差
def cal_corrcoef(float_df, y_train):
    corr_values = []
    float_col = list(float_df.columns)
    for col in float_col:
        corr_values.append(abs(np.corrcoef(float_df[col].values, y_train) \
                                   [0, 1]))
    corr_df = pd.DataFrame({'col': float_col, 'corr_value': corr_values})
    corr_df = corr_df.sort_values(by='corr_value', ascending=False)
    return corr_df


# 去掉数字相同的列以及日期列
def remove_waste_col(data):
    columns = list(data.columns)
    same_num_col = []
    for col in columns:
        max_num = data[col].max()
        if max_num != data[col].min() and str(max_num).find('2017') == -1 and str(max_num).find('2016') == -1:
            same_num_col.append(col)
    return data[same_num_col]


def normalize_data(data):
    return data.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
    # return preprocessing.scale(data, axis=0)


def create_model(x_train, y_train):
    print("begin to train...")
    model = LinearRegression()
    model.fit(x_train, y_train)
    return model


def cal_MSE(y_predict, y_real):
    n = len(y_predict)
    print("样本数量:" + str(n))
    return np.sum(np.square(y_predict - y_real)) / n

if __name__ == '__main__':
    x_train, y_train, x_test = pre_process_data()
    model = create_model(x_train, y_train)
    print("交叉验证...")
    scores = cross_validation.cross_val_score(model, x_train, y_train, cv = 10, scoring='neg_mean_squared_error')
    print(scores)
    ans = model.predict(x_test)
    sub_df = pd.read_csv('train_test.csv', header=None)
    sub_df['Y'] = ans
    sub_df.to_csv('final_test.csv', header=None, index=False)
    print("MSE:")
    print(cal_MSE(ans, y_train))