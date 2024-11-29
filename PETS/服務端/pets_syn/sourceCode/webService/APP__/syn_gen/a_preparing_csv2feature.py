##20180919

import numpy as np
import pandas as pd
import pickle
import csv
from sklearn import preprocessing
import random
import os

def csv2dicts(csvfile):
    data = []
    keys = []
    for row_index, row in enumerate(csvfile):
        if row_index == 0:
            keys = row
            #print(row)
            continue
        data.append({key: value for key, value in zip(keys, row)})
    return data

def feature_list(record,col_name):
    list_of_all = []
    for col_name_id in col_name: 
#         print(col_name_id)
        #print(len(record[col_name_id]))
        list_of_all.append(record[col_name_id])       
    return list_of_all
# [workclass education education_num marital_status occupation relationship race sex native_country class]

def csv2feature(directory,datapath, col_name, tar_colname, transfer):

    with open(datapath, encoding='utf-8') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        with open(os.path.join(directory,'pkl','train_data.pickle'), 'wb') as f:
            data = csv2dicts(data)
            data = data[::-1]
            pickle.dump(data, f, -1)
            #print(data[0])
            
    with open(os.path.join(directory,'pkl','train_data.pickle'), 'rb') as f:
        train_data = pickle.load(f)
        num_records = len(train_data)
    
    #data = pd.read_csv(args['dataset'],header=0)

    train_data_X = []
    train_data_y = []
    for record in train_data:
        train_data_X.append(feature_list(record,col_name))
        #print(train_data_X.type)
        train_data_y.append(record[tar_colname]) #parameter: target
    
    full_X = train_data_X
    full_X = np.array(full_X)
    train_data_X = np.array(train_data_X)
    
    #print(train_data_X.shape)
    
    les = []
    for i in range(train_data_X.shape[1]):
        le = preprocessing.LabelEncoder()
        le.fit(full_X[:, i].astype(str))
        les.append(le)
        train_data_X[:, i] = le.transform(train_data_X[:, i].astype(str))
    
    if transfer == "True":
        le = preprocessing.LabelEncoder()
        le.fit(np.array(train_data_y).astype(str))
        train_data_y = le.transform(np.array(train_data_y).astype(str))
        train_data_y= train_data_y.astype(float)
        print (train_data_y[:10])
    
        #print ("TRANSFERING")
    
        for i in range(len(train_data_y)):
            if train_data_y[i] == 0.0: #' >50K': ## parameter:class
                train_data_y[i] =  0.1 #random.randint(50000,100000)
            else:
                train_data_y[i] =  0.9*train_data_y[i] #random.randint(0,50000)
    
    elif transfer == "False":
        #print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
        train_data_y= np.array(train_data_y).astype(int)
        for i in range(len(train_data_y)):
            if train_data_y[i] == 0.0: #' >50K': ## parameter:class
                train_data_y[i] =  0.1 #random.randint(50000,100000)
            else:
                train_data_y[i] =  0.9*train_data_y[i] #random.randint(0,50000)
        
    
#     print(train_data_y[:10])
    
    with open(os.path.join(directory,'pkl','les.pickle'), 'wb') as f:
        pickle.dump(les, f, -1)
#     print(les[0])

    with open(os.path.join(directory,'pkl','feature_train_data.pickle'), 'wb') as f:
        pickle.dump((train_data_X, train_data_y), f, -1)
    print(train_data_X[0], train_data_y[0])
    print("a_preparing_csv2feature finished!")

    ####command: python 1_a_preparing_csv2feature.py -d adult.csv -col workclass education education_num marital_status occupation relationship race sex native_country class -tar_col class -transfer False
