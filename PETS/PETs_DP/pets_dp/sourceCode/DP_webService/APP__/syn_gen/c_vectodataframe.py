
# coding: utf-8

import pandas as pd
import numpy as np
import pickle


def vec2dataframe(directory,data,col_name,conti_col):

#     data = pd.read_csv(path,header=0)
    
    class_embedding = []
    with open(directory+"pkl/embeddings.pickle", 'rb') as f:
          class_embedding = pickle.load(f)
    #print(len(class_embedding))
    
    with open(directory+"pkl/les.pickle", 'rb') as f:
        les = pickle.load(f)
    
    
#     class_key = list(les[0].classes_)
#     print(len(class_key))
    
    df_embedded = pd.DataFrame()
    for idx in range(len(col_name)):
        work_vec=[]
        work = data[col_name[idx]].tolist()

       
        class_name = les[idx]
        class_embeddig = class_embedding[idx]
        #print(col_name[idx])
        for i in range(len(work)):
            for j in range(len(list(class_name.classes_))):
                if str(work[i]) == str(list(class_name.classes_)[j]):
                    work_vec.append(class_embeddig[j])
                    break
        
        work_vec = np.array(work_vec)
#         print(work_vec.shape)
        workclass = pd.DataFrame(work_vec, columns=[col_name[idx]+str(k) for k in range(work_vec.shape[1]) ])
        df_embedded =  pd.concat( [df_embedded,workclass], axis=1)
    #print(df_embedded.shape)
    _, sum_col = df_embedded.shape
    
#     if conti_col == "all":
#         conti_col_list = list(data._get_numeric_data().columns)#define numerical type attribute
#         common = list(set(conti_col_list)&set(col_name))
#         conti_col_name = list(set(conti_col_list)-set(common))
#         conti_col = conti_col_name
#         conti_col_name = list(set(data.columns.tolist())^set(col_name))
#     else:
#         conti_col_name = list(data._get_numeric_data().columns)
        
    df_embedded =  pd.concat( [df_embedded,data[conti_col]], axis=1)
    #print(df_embedded.head())
    #print(df_embedded.shape)
    df_embedded.to_csv(directory+"pkl/test_category_conti.csv", header=True, index= None)
    #print("step3:  ",df_embedded.columns.tolist())
    return sum_col