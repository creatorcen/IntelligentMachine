# encoding = utf-8

import pandas as pd
import numpy as np
from sklearn import preprocessing


def pre_process_data():
    print("begin to read data")
    train_data = pd.read_excel('small.xlsx')
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
    print("Finish preprocess")
    print(x_train.shape, y_train.shape)
    return x_train, y_train


def remove_nan_data(data):
    nan_data = data.isnull().sum(axis=0).reset_index()
    nan_data.columns = ['col', 'nan_count']
    nan_data = nan_data.sort_values(by='nan_count')
    nan_data_value = nan_data[nan_data.nan_count > 20].col.values
    print("nan_data_value:" + str(nan_data_value))
    return nan_data_value


#  删除非数字行
def remove_no_float(data):
    data_type = data.dtypes.reset_index()
    data_type.columns = ['col', 'dtype']
    return data_type[data_type.dtype != 'object'].col.values


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


if __name__ == '__main__':
    x_train, y_train = pre_process_data()
