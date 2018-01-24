import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from main import remove_waste_col, remove_miss_row, remove_miss_col, remove_no_float
from main import remove_no_float
import numpy as np
from sklearn import preprocessing
from sklearn import utils


def remove_wrong_row(small_data):
    nan_data1 = small_data.isnull()
    nan_data2 = nan_data1.sum(axis=0)
    nan_data3 = nan_data2.reset_index()
    nan_data3.columns = ['col', 'nan_count']
    nan_data = nan_data3.sort_values(by='nan_count')
    nan_data_value = nan_data[nan_data.nan_count > 5].col.values
    small_data.drop(nan_data_value, axis=1, inplace=True)
    data = remove_no_float(small_data)
    small_data = small_data[data]
    small_data.fillna(small_data.mean(), inplace=True)

    data1 = small_data.append(small_data.mean() + 3 * small_data.std(), ignore_index=True)
    data2 = data1.append(small_data.mean() - 3 * small_data.std(), ignore_index=True)
    upper = small_data.mean() + 3 * small_data.std()
    lower = small_data.mean() - 3 * small_data.std()

    wrong_data1 = (small_data > upper).sum(axis=1).reset_index()
    wrong_data1.columns = ['row', 'na_count']
    wrong_row1 = wrong_data1[wrong_data1.na_count >= 3].row.values

    wrong_data2 = (small_data < lower).sum(axis=1).reset_index()
    wrong_data2.columns = ['row', 'na_count']
    wrong_row2 = wrong_data2[wrong_data2.na_count >= 3].row.values
    wrong_row = np.concatenate((wrong_row1, wrong_row2))

    print(small_data.shape)
    small_data.drop(wrong_row, axis=0, inplace=True)
    print(wrong_row1)
    wrong_data2 = wrong_data1[wrong_data1 > lower]
    print(small_data.shape)


def change_object_to_float(data):
    print(data.shape)
    data_type = data.dtypes.reset_index()
    data_type.columns = ['col', 'dtype']
    set_object = set('A')
    dict_object = {}
    data_object_col = data_type[data_type.dtype == 'object'].col.values
    data_object = data[data_object_col]
    i = 0.0
    for object in data_object:
        set_object = set(data_object[object].values) | set_object
        print(set_object)
    for item in set_object:
        dict_object[item] = i
        i += 1.0
    print(dict_object)
    for col in data_object_col:
        for i in range(len(data[col].values)):
            data[col].values[i] = dict_object[data[col].values[i]]
    # for col in data_object_col:
    #     data[col].values = list(map(lambda x: dict_object[x], list(data[col].values)))

    # data_object.apply(lambda x: dict_object[x])

    # data.to_excel("half_data/data_to_float.xlsx")
    return data


def do_lda(x_train, y_train):
    print("Begin LDA。。。")
    lab_enc = preprocessing.LabelEncoder()
    encoded = lab_enc.fit_transform(y_train)
    print(utils.multiclass.type_of_target(y_train))
    print(utils.multiclass.type_of_target(encoded))
    print(encoded)
    lda = LinearDiscriminantAnalysis(n_components=10)
    lda.fit(x_train, encoded)
    x_train_new = lda.transform(x_train)
    # x_train_new.to_csv('lda_train.csv', header=None, index=False)
    print(x_train_new)
    return x_train_new


def stack_data():
    y = pd.read_excel('raw_data/small.xlsx')
    y = y['Y'].values
    print(y.shape)
    y_a = pd.read_csv('raw_data/test_a_ans.csv', header=None)
    y_a = y_a[1].values
    print(y_a.shape)
    Y = np.vstack((y, y_a))
    print(Y)


def knn_fill_nan(data, K):
    print("raw_data shape:", data.shape)
    col_values = remove_no_float(data)
    data = data[col_values]
    print("remove no float col shape: ", data.shape)

    # 计算每一行的空值，如有空值则进行填充，没有空值的行用于做训练数据
    data_row = data.isnull().sum(axis=1).reset_index()
    data_row.columns = ['raw_row', 'nan_count']
    # 空值行（需要填充的行）
    data_row_nan = data_row[data_row.nan_count > 0].raw_row.values

    # 非空行 原始数据
    data_no_nan = data.drop(data_row_nan, axis=0)

    # 空行 原始数据
    data_nan = data.loc[data_row_nan]
    for row in data_row_nan:
        data_row_need_fill = data_nan.loc[row]
        # 找出空列，并利用非空列做KNN
        data_col_index = data_row_need_fill.isnull().reset_index()
        data_col_index.columns = ['col', 'is_null']
        is_null_col = data_col_index[data_col_index.is_null == 1].col.values
        data_col_no_nan_index = data_col_index[data_col_index.is_null == 0].col.values
        # 保存需要填充的行的非空列
        data_row_fill = data_row_need_fill[data_col_no_nan_index]

        # 广播，矩阵 - 向量
        data_diff = data_no_nan[data_col_no_nan_index] - data_row_need_fill[data_col_no_nan_index]
        # 求欧式距离
        # data_diff = data_diff.apply(lambda x: x**2)
        data_diff = (data_diff ** 2).sum(axis=1)
        data_diff = data_diff.apply(lambda x: np.sqrt(x))
        data_diff = data_diff.reset_index()
        data_diff.columns = ['raw_row', 'diff_val']
        data_diff_sum = data_diff.sort_values(by='diff_val', ascending=True)
        data_diff_sum_sorted = data_diff_sum.reset_index()
        # 取出K个距离最近的row
        top_k_diff_row = data_diff_sum_sorted.loc[0:K - 1].raw_row.values
        # 根据row 和 col值确定需要填充的数据的具体位置（可能是多个）
        # 填充的数据为最近的K个值的平均值
        top_k_diff_val = data.loc[top_k_diff_row][is_null_col].sum(axis=0) / K

        # 将计算出来的列添加至非空列
        data_row_fill = pd.concat([data_row_fill, pd.DataFrame(top_k_diff_val)]).T
        print(data_no_nan.shape)
        data_no_nan = data_no_nan.append(data_row_fill, ignore_index=True)
        print(data_no_nan.shape)
    return data_no_nan


if __name__ == '__main__':
    small_data = pd.read_excel('small.xlsx')
    print(small_data.shape)
    small_data.drop(['ID'], axis=1, inplace=True)
    # remove_wrong_row(small_data)
    small_data = change_object_to_float(small_data)
    # small_data.fillna(small_data.median(), inplace=True)
    small_data = remove_waste_col(small_data)
    # x_train = small_data.drop(['Y'], axis=1)
    # y_train = small_data['Y']
    # x_train = do_lda(x_train.values, y_train.values)
    small_data = remove_miss_col(small_data)
    small_data = remove_miss_row(small_data)
    small_data = knn_fill_nan(small_data, 9)
    small_data.to_excel('small_data2.xlsx')
    # stack_data()
