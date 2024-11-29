import pandas as pd
import numpy as np
from scipy import spatial
import pickle
from sklearn import preprocessing
import random
import os
import math
from keras.models import load_model
def some(x, n):
    return x.ix[random.sample(x.index, n)]

def recovering(original, dataset,sum_col_num):
    #original = np.loadtxt("wine.csv", delimiter=",")
     original = np.array(original)
     row,col = original.shape
     org_data = original[:,sum_col_num:col]#-1]
     max_val=np.max(org_data,axis=0)
     min_val=np.min(org_data,axis=0)
     xx = (dataset-(-1))/(1-(-1))*(max_val-min_val)+min_val
     return xx

def sampling(directory,sum_col_num,epoch=120):
    dir_syn=os.path.join(directory,'sample')
    if not os.path.exists(dir_syn):
        os.mkdir(dir_syn)
    generator_decoder = load_model(os.path.join(directory,'models','gan_generator_epoch_'+str(epoch)+'.h5') )##Feedback???
    #print("epoch: ",epoch)
    original = pd.read_csv(os.path.join(directory,'pkl/test_category_conti.csv'),header=0, encoding='utf-8')
    examples, randomDim =  original.shape
    
    #gen_row = 21000 #examples*1.002
    gen_row = examples*1.002

    df = pd.DataFrame()
    for _ in range(15):
    #while True:
        noise = np.random.normal(0, 1, size=[examples, randomDim])
        generatedImages = generator_decoder.predict(noise)
        class2 = generatedImages.reshape(examples,randomDim)
        df1 = pd.DataFrame(class2)

        df1_slice_tail = recovering(original,np.clip(np.array(df1)[:,sum_col_num:randomDim], -1, 1), sum_col_num)
        #df1_slice_tail = recovering(original,np.array(df1.iloc[:,sum_col_num:randomDim]),sum_col_num)
        df1_slice_tail = pd.DataFrame(df1_slice_tail)

        df_slice_1 = df1.iloc[:,0:sum_col_num]
        df1 = pd.concat([df_slice_1, df1_slice_tail],axis=1)
        df1 = df1.rename(columns={x:y for x,y in zip(df1.columns,range(0,len(df1.columns)))})

        #for i in range(randomDim-sum_col_num):
        #    df1 = df1[df1.iloc[:,sum_col_num+i]>=0.0] #'Age'
    
        #print(df1.shape)
        df= pd.concat([df, df1],axis=0)
        print("Concat: ",df.shape)
        if (df.shape[0]>int(gen_row)):
            break
    df = df.take(np.random.permutation(len(df))[:int(gen_row)])
    #print(df.shape)
    if df.shape[0]>0:
        df.to_csv(os.path.join(directory,'sample','synthetic_sample_'+str(epoch)+'.csv'),float_format='%.7f',index=False,header=False, encoding='utf-8')
        return 'True'
    else:
        return 'False'

def eudis5(v1, v2):
    dist = [(a - b)**2 for a, b in zip(v1, v2)]
    dist = math.sqrt(sum(dist))
    return dist    

def recovering_syn(directory,sum_col_num,col_name,conti_col,e):
    dir_syn=os.path.join(directory,'transform')
    if not os.path.exists(dir_syn):
        os.mkdir(dir_syn)
    fake_data = pd.read_csv(os.path.join(directory,"sample","synthetic_sample_"+str(e)+'.csv'), header=None, encoding="utf-8")
    class_embedding = []
    with open(os.path.join(directory,"pkl","embeddings.pickle"), 'rb') as f:
          class_embedding = pickle.load(f)
    #print(len(class_embedding))
    
    space = []
    for i in range(len(class_embedding)):
        space.append(class_embedding[i].shape[1])
    #print(space)
    
    with open(os.path.join(directory,"pkl","les.pickle"), 'rb') as f:
        les = pickle.load(f)
    
#     recover_fake_data = pd.read_csv(path,header=0)[col_name]#pd.DataFrame()
    recover_fake_data = pd.DataFrame(columns=col_name)
    
    for idx in range(len(col_name)):
        col_name_idx = str(col_name[idx])
        
        up = 0
        down = space[idx]
        if idx == 0:
            up = 0
        else: 
            for up_i in range(idx):
                up = up + int(space[up_i])
        down = int(up+down)
        #print(up,down)
        Pclass_vec = fake_data.iloc[:,up:down].values
        #print(Pclass_vec.shape)
        
        listofclass = list(les[idx].classes_) ##Pclass:les[idx]

        fake_Pclass =[]
        len_col = len(class_embedding[idx])
        iidx = idx
        
        for k in range(Pclass_vec.shape[0]):
            dist=float("inf")
            values = []
            for j in range(len_col): ##Pclass_embedding:class_embedding
                
                P_vec = Pclass_vec[k]
                vec = class_embedding[iidx][j]
                
#                 d = np.linalg.norm(P_vec-vec) #according to paper, 以歐式距離計算
                d = eudis5(P_vec, vec)
#                 values.append(d) 
#                 idx = values.index(min(values))
                if dist > d:
                    dist = d
                    idx = j
            fake_Pclass.append(listofclass[idx])
        #se = pd.Series(fake_Pclass)
        recover_fake_data[col_name_idx] = fake_Pclass#se.values
    
#     data = pd.read_csv(directory+'test_category_conti.csv',header=0)
    #print("test_category_conti:",data.columns.tolist())
    
#     if conti_col == "all":    
# #         conti_col_name = list(set(data.columns.tolist())^set(col_name))
#         conti_col_list = list(data._get_numeric_data().columns)#define numerical type attribute
#         common = list(set(conti_col_list)&set(col_name))
#         conti_col_name = list(set(conti_col_list)-set(common))
#         conti_col = conti_col_name
    
    conti_dim = sum_col_num
#     conti_col_name = data.columns.tolist()[conti_dim:data.shape[1]]
    #print("conti_col_name",conti_col_name)
    for conti_col_name_idx in conti_col:
        recover_fake_data[conti_col_name_idx]= fake_data.iloc[:,conti_dim:conti_dim+1]
        recover_fake_data[conti_col_name_idx]=recover_fake_data[conti_col_name_idx].astype('int')
        conti_dim = conti_dim + 1
        #print(conti_dim)
    
    #print("recover shape: ",recover_fake_data.shape)    
#     print(recover_fake_data.head())
    recover_fake_data.to_csv(os.path.join(directory,'transform','synthetic_transform_'+str(e)+'.csv'),index=False,header=True, encoding='utf-8')    
    
