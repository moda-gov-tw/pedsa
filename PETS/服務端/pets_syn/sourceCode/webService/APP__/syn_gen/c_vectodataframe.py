
# coding: utf-8

import pandas as pd
import numpy as np
import pickle
import os

def vec2dataframe(directory,data,col_name,conti_col):

#     data = pd.read_csv(path,header=0)
    
    class_embedding = []
    with open(os.path.join(directory,"pkl","embeddings.pickle"), 'rb') as f:
          class_embedding = pickle.load(f)
    #print(len(class_embedding))
    
    with open(os.path.join(directory,"pkl","les.pickle"), 'rb') as f:
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

        
    df_embedded =  pd.concat( [df_embedded,data[conti_col]], axis=1)
    df_embedded.to_csv(os.path.join(directory,"pkl","test_category_conti.csv"), header=True, index= None)
    return sum_col