# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from .Base import load_p
## Comparison index function

# def pq_match(p, q):
#     count = 0.0
#     for i in range(len(q)):
#         if p[i] == q[i]:
#             count += 1
#     return count / len(q)

#20200213更新
def pq_match(p, q):
    count = 0.0
    if len(q) == 0:
        return 0.0
    else:
        for i in range(len(q)):
            if p[i] == q[i]:
                count += 1
        return count / len(q)


def get_GroupDict(self):
    ## 得到分群結果
    Group = self.df_ori.groupby(self.QI)  # 把原始資料集根據QI做分群
    GroupDict = Group.groups    # 轉成dict型態
    # GroupKey = list(GroupDict.keys())  # 得到dict的key
    return GroupDict

def get_df_sum(self):
    ### summation 
    df_ori_sum = self.df_ori[self.QI].copy()
    df_ano_sum = self.df_ano[self.QI].copy()
    d_osum = self.df_ori.sum(axis=1)
    d_asum = self.df_ano.sum(axis=1)
    df_ori_sum['sum'] = d_osum
    df_ano_sum['sum'] = d_asum
    return df_ori_sum, df_ano_sum

class get_security(object):

    def __init__(self, df_ori, df_ano, attribute, SA, QI, p, detail_setting ):
        self.df_ori = df_ori
        self.df_ano = df_ano
        self.attribute = attribute
        self.SA = SA
        self.QI = QI
        self.p = p
        self.GroupDict = get_GroupDict(self)
        self.df_ori_sum, self.df_ano_sum = get_df_sum(self)
        self.detail_setting = detail_setting

    def S3(self):
        # method: S3-IdRand
        # 從同個集合隨機猜測Index
        #

        I_idrand = []
        for i in range(len(self.df_ano)):   
            labels = tuple(self.df_ano[self.QI].iloc[i])   # 得到 df_ano第 i行的 QI
            if labels in self.GroupDict:
                _idx = np.random.randint(len(self.GroupDict[labels]))  # 從同個集合rand一個 int 
                idx = self.GroupDict[labels][_idx]  #　把該 int對應成行號
                I_idrand.append(idx)   # 把行號記錄起來

        # print("method S3-IdRand risk: {}%".format(pq_match(self.p, I_idrand)*100))
        return pq_match(self.p, I_idrand)*100


    def S4_SA(self):
        # method: S4-IdSA
        # 根據某SA值差異最小的Index來猜測
        # 根據相同的QI集合，找第i比

        if self.detail_setting:
            tgt_clmn = input("S4, Input the target attribute: ")
        else:
            tgt_clmn = self.SA[0]

        I_idsa = []
        for i in range(len(self.df_ano)):  
            labels = tuple(self.df_ano[self.QI].iloc[i])   # 得到 df_ano第 i行的 QI
            if labels in self.GroupDict:
                idx = (np.abs(self.df_ori[tgt_clmn][self.GroupDict[labels]] - self.df_ano[tgt_clmn][i])).idxmin()+1   # 找SA值差異最小的index
                I_idsa.append(idx) 
            
        # print("method S4-IdSA risk: {}%".format(pq_match(self.p, I_idsa)*100)) 
        return pq_match(self.p, I_idsa)*100


    def S4_summation(self):
        # method: S4-IdSA summation
        # 根據全部SA值差異最小的Index來猜測
        #

        I_idsa_sum = []
        tgt_clmn = 'sum'

        for i in range(len(self.df_ano)):  
            labels = tuple(self.df_ano[self.QI].iloc[i])   # 得到 df_ano第 i行的 QI
            if labels in self.GroupDict:
                idx = (np.abs(self.df_ori_sum[tgt_clmn][self.GroupDict[labels]] - self.df_ano_sum[tgt_clmn][i])).idxmin()+1  # 找SA值差異最小的index
                I_idsa_sum.append(idx) 
            
        # print("method S4-IdSA summation risk: {}%".format(pq_match(p, I_idsa_sum)*100)) 
        return pq_match(self.p, I_idsa_sum)*100

    def S5(self):
        # method: S5-Sort summation
        # 根據匿名後的行號順序，猜測排序後所對應的Index
        #

        I_idsort = []
        tgt_clmn = 'sum'

        sort_ori = self.df_ori_sum.sort_values(tgt_clmn, axis=0) ## 根據SA值總合做排序
        sort_ano = self.df_ano_sum.sort_values(tgt_clmn, axis=0) 

        print ('sort_ori')
        print (sort_ori)
        print ('sort_ano')
        print (sort_ano)

        #20200207程序錯誤
        try:
            match = pd.DataFrame({'ori_index' : list(sort_ori.index), 'ano_index' : list(sort_ano.index)}) ## 把排序後的順序加到 Dataframe
            print ('match')
            print (match)
            I_idsort = list(match.sort_values('ano_index', axis=0)['ori_index'])  ## 根據匿名後的行號順序，猜測排序後所對應的Index
            I_idsort = list(map(lambda x: x+1, I_idsort))
                    
            # print("method S5-Sort-summation risk: {}%".format(pq_match(p, I_idsort)*100)) 
            return pq_match(self.p, I_idsort)*100
        except Exception as e:
            print ("S5 error:getRiskAnalysis:"+str(e))


    def S6(self):
        # method: S6-Sort Attribute
        # 根據匿名後的行號順序，猜測排序後所對應的Index
        
        if self.detail_setting:
            tgt_clmn = input("S6, Input the target attribute: ")
        else:
            tgt_clmn = self.SA[0]

        I_sa = []
        sort_ori = self.df_ori.sort_values((tgt_clmn), axis=0)  ## 根據SA值做排序
        sort_ano = self.df_ano.sort_values(tgt_clmn, axis=0)
        match = pd.DataFrame({'ori_index' : list(sort_ori.index), 'ano_index' : list(sort_ano.index)}) ## 把排序後的順序加到 Dataframe
        I_sa = list(match.sort_values('ano_index', axis=0)['ori_index']) ## 根據匿名後的行號順序，猜測排序後所對應的Index
        I_sa = list(map(lambda x: x+1, I_sa))
                    
        # print("method S6-Sort-SA1 risk: {}%".format(pq_match(p, I_sa)*100)) 
        return pq_match(self.p, I_sa)*100


