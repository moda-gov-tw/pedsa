import pandas as pd
import os
from sklearn import preprocessing
from scipy.stats import entropy

def check_type(col_name,path,keyName):
    
    df = pd.read_csv(path,header=0)
    df =df.drop(keyName, axis=1)
    conti_col = list(set(df.columns.tolist())^set(col_name))
   
    for keyID in keyName:
        if keyID in conti_col:
            conti_col.remove(keyID)
        if keyID in col_name:
            col_name.remove(keyID)

    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    
    ob_col = []
    co_name = df_numeric.columns.tolist()
    for col in co_name:
        f_nan_sum = df_numeric[col].isnull().sum()
        if f_nan_sum >= int(df_numeric.shape[0]*0.9):
            ob_col.append(col)
            
#     print("Obeject cols: "+str(ob_col)+"\n")
    non_conti = []
    for non_ in conti_col:
        if non_ in ob_col:
            non_conti.append(non_)
#     print ("***Identify these attributes type are categorical: "+str(non_conti)+"\n")
    for non_ in non_conti:   
        col_name.append(non_)
        conti_col.remove(non_)
#     print("Categorical attribute:"+str(col_name)+"\n")
#     print("Continuous attribute:"+str(conti_col)+"\n")
   
    df.loc[:, conti_col] = df.loc[:, conti_col].replace('NaN',0) 

    ##cal attribute (#.unique)
    unique_att_num = []  
    for i in range(len(col_name)): 
        col_name_id = col_name[i]
        unique_att_num.append(df[col_name_id].value_counts().size)
#     print(unique_att_num)
    
    ##calculate target column: 
    ##categorical attr with min entropy as target
    df_encode = pd.DataFrame()
    le = preprocessing.LabelEncoder()
    for idx in ob_col:
        le.fit(df[idx])
        df_encode[idx] = le.transform(df[idx])
    ###correlation spearman
#    corr_matrix = df_encode.corr(method='spearman').abs()
#    corr = []
#    for i in range(corr_matrix.shape[0]):
#        corr.append(corr_matrix.iloc[i].sum()/corr_matrix.shape[0])
#    max_corr = corr.index(max(corr))
#    ob = corr_matrix.columns.tolist()
#    tar_col = ob[max_corr]
    ### min entropy
    values = list(entropy(df_encode)) 
    id_min_entropy = values.index(min(values))
    tar_col = ob_col[id_min_entropy]
    return col_name, conti_col, unique_att_num, tar_col, df

def hit_rate(directory,df,e,conti_col):
#     df = pd.read_csv(path,header=0)

    df_fake = pd.read_csv(directory+'transform/synthetic_transform_'+str(e)+'.csv' ,header=0)
    
    
    all_attri = df.columns.tolist()
    print(all_attri)
    
    # conti_col = list(df._get_numeric_data().columns)
    for conti_col_name in conti_col:
        df[conti_col_name] = df[conti_col_name].astype(int)
        df_fake[conti_col_name] = df_fake[conti_col_name].astype(int)
    
    df_gb_all = df.groupby(all_attri).size().to_frame('count_org').reset_index()
    df_fake_gb_all = df_fake.groupby(all_attri).size().to_frame('count_syn').reset_index()

    common_all = df_fake_gb_all.merge(df_gb_all) #取合成和真實的共同部分

    fake_common_all = pd.concat([df_fake_gb_all, common_all],axis=0, ignore_index=True) #假的和共同的合併
#     fake_common_all =fake_common_all.reset_index(drop=True)
    
    fake_uniqu_all = fake_common_all.drop_duplicates(subset=all_attri,keep=False) #把合成資料沒有碰撞到的取出來

    unique_rate_all = fake_uniqu_all['count_syn'].sum()/df_fake_gb_all['count_syn'].sum()*100 #合成資料獨特沒有碰撞的
    hit_rate_all = 100-unique_rate_all
    print ("UNIque rate:",unique_rate_all,"%")
    print("HIT rate:",hit_rate_all,"%")
    print('After drop: ',fake_uniqu_all['count_syn'].sum(),df_gb_all['count_org'].sum() )
    print('Duplicate rows:',common_all.head(1))
    print('#. duplicated: ',df_fake_gb_all['count_syn'].sum()-fake_uniqu_all['count_syn'].sum())
    print('------------------------')   
    print('df_fake.shape:', df_fake.shape)
    common_ = common_all.iloc[:,:df_fake.shape[1]]
    print('df_fake_common.shape:', common_.shape)
    print('#. duplicated: ',df_fake_gb_all['count_syn'].sum()-fake_uniqu_all['count_syn'].sum())
    print('------------------------')    
   
    fake_rm_hit = df_fake[~df_fake.apply(tuple,1).isin(common_.apply(tuple,1))]
    if df.shape[0] >=  fake_rm_hit.shape[0]:
        rows = fake_rm_hit.shape[0]
        print('Too many hit records!')
        os.remove(directory+'transform/synthetic_transform_'+str(e)+'.csv')
        os.remove(directory+'sample/synthetic_sample_'+str(e)+'.csv')
    else:
        rows = df.shape[0]
        fake_rm_hit_subset = fake_rm_hit.sample(n=rows)
        fake_rm_hit_subset.to_csv(directory+'synthetic/synthetic_transform_rmhit'+str(e)+'.csv',index=False,header=True)  
        print ("Finished dropping the duplicated rows:",fake_rm_hit_subset.shape)
    
