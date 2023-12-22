import pandas as pd
import numpy as np
from scipy import spatial
import pickle
from sklearn import preprocessing
import random
from keras.models import load_model
import os
def some(x, n):
    return x.ix[random.sample(x.index, n)]

def recovering_conti(original, dataset):
    #original = np.loadtxt("wine.csv", delimiter=",")
     original = np.array(original)
     row,col = original.shape
     org_data = original[:,0:col]#-1]
     max_val=np.max(org_data,axis=0)
     min_val=np.min(org_data,axis=0)
     xx = (dataset-(-1))/(1-(-1))*(max_val-min_val)+min_val
     return xx

def sampling_conti(directory,filepath,sum_col_num,epoch=120):
    dir_syn=(directory+'sample/')
    if not os.path.exists(dir_syn):
        os.mkdir(dir_syn)
    generator_decoder = load_model(directory+'models/gan_generator_epoch_'+str(epoch)+'.h5') ##Feedback???
    #print("epoch: ",epoch)
    original = pd.read_csv(filepath,header=0)
    examples, randomDim =  original.shape
    
    df = pd.DataFrame()
    while True:
        noise = np.random.normal(0, 0.5, size=[examples, randomDim])
        generatedImages = generator_decoder.predict(noise)
        class2 = generatedImages.reshape(examples,randomDim)
        df1 = pd.DataFrame(class2)
        
        df1_recover = recovering_conti(original,np.array(df1.iloc[:,0:randomDim]))
        df1_recover = pd.DataFrame(df1_recover)
#         df1_slice_tail = recovering(original,np.array(df1.iloc[:,sum_col_num:randomDim]),sum_col_num)
#         df1_slice_tail = pd.DataFrame(df1_slice_tail)

#         df_slice_1 = df1.iloc[:,0:sum_col_num]
#         df1 = pd.concat([df_slice_1, df1_slice_tail],axis=1)
#         df1 = df1.rename(columns={x:y for x,y in zip(df1.columns,range(0,len(df1.columns)))})

#         for i in range(randomDim-sum_col_num):
#             df1 = df1[df1.iloc[:,sum_col_num+i]>=0.0] #'Age'
    
        print(df1.shape)
        df= pd.concat([df, df1_recover],axis=0)
        print("Concat: ",df.shape)
        if (df.shape[0]>examples):
            break
    df = df.take(np.random.permutation(len(df))[:int(examples*1.002)])
    #print(df.shape)
    df.columns = original.columns.tolist()
    df.to_csv(directory+'transform/synthetic_transform_'+str(epoch)+'.csv',float_format='%.7f',index=False,header=True)

    
