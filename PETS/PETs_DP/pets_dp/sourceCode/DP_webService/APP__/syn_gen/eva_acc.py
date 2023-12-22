import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import category_encoders as ce
import itertools
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export
from sklearn import preprocessing,metrics, cross_validation, svm
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
import os

def acc(directory,path,col_name,tar_col,e):
    df = pd.read_csv(path,header=0)

    df_fake = pd.read_csv(directory+'synthetic/synthetic_transform_rmhit'+str(e)+'.csv' ,header=0)
    if df_fake[tar_col].value_counts().size == 1:
        kpi = "NO"
        os.remove(directory+'synthetic/synthetic_transform_rmhit'+str(e)+'.csv')
        os.remove(directory+'transform/synthetic_transform_'+str(e)+'.csv')
        os.remove(directory+'sample/synthetic_sample_'+str(e)+'.csv')
        
    else:      
        fake_y = df_fake[tar_col]
        fake_X = df_fake.drop([tar_col], 1)

        y = df[tar_col]   
        cols = df_fake.columns.tolist()
        df = df[cols]
        X = df.drop([tar_col], 1)
        #print('cols:',cols)

        df_y= pd.concat([fake_y,y],axis=0)
        le = preprocessing.LabelEncoder()
        le.fit(np.array(df_y))
        train_data_y = le.transform(np.array(df_y))
    #     train_data_y= train_data_y.astype(float)
        fake_y = train_data_y[:len(fake_y)]
        y = train_data_y[len(y):]

        col_name_without_target = list(set(col_name)-set([tar_col])-set(['mo_date_account_created','yr_date_account_created']))
        #print('col_name_without_target:',col_name_without_target)
        df= pd.concat([fake_X,X],axis=0)
        enc = ce.OrdinalEncoder(cols=col_name_without_target,impute_missing=False).fit(df)
        # transform the dataset
        onehotencoder_dataset = enc.transform(df)
        
        fake_X = onehotencoder_dataset[:len(fake_y)]
        X = onehotencoder_dataset[len(y):]
        
        # Logistic Regression
        logreg = LogisticRegression()
        logreg.fit(fake_X, fake_y)
        acc_log = round(logreg.score(X, y) * 100, 2)
        logreg.fit(X, y)
        acc_log_r = round(logreg.score(X, y) * 100, 2)    

        # Support Vector Machines
#         svc = SVC()
#         svc.fit(fake_X, fake_y)
#         acc_svc = round(svc.score(X, y) * 100, 2)
#         svc.fit(X, y)
#         acc_svc_r = round(svc.score(X, y) * 100, 2)

        #KNN
        knn = KNeighborsClassifier(n_neighbors = 3)
        knn.fit(fake_X, fake_y)
        acc_knn = round(knn.score(X, y) * 100, 2)
        knn.fit(X, y)
        acc_knn_r = round(knn.score(X, y) * 100, 2)

        #Gaussian Naive Bayes
        gaussian = GaussianNB()
        gaussian.fit(fake_X, fake_y)
        acc_gaussian = round(gaussian.score(X, y) * 100, 2)
        gaussian.fit(X, y)
        acc_gaussian_r = round(gaussian.score(X, y) * 100, 2)

        # Perceptron
        perceptron = Perceptron()
        perceptron.fit(fake_X, fake_y)
        acc_perceptron = round(perceptron.score(X, y) * 100, 2)
        perceptron.fit(X, y)
        acc_perceptron_r = round(perceptron.score(X, y) * 100, 2)

        # Linear SVC
        linear_svc = LinearSVC()
        linear_svc.fit(fake_X, fake_y)
        acc_linear_svc = round(linear_svc.score(X, y) * 100, 2)
        linear_svc.fit(X, y)
        acc_linear_svc_r = round(linear_svc.score(X, y) * 100, 2)

        # Stochastic Gradient Descent
        sgd = SGDClassifier()
        sgd.fit(fake_X, fake_y)
        acc_sgd = round(sgd.score(X, y) * 100, 2)
        sgd.fit(X, y)
        acc_sgd_r = round(sgd.score(X, y) * 100, 2)

        # Decision Tree
        decision_tree = DecisionTreeClassifier()
        decision_tree.fit(fake_X, fake_y)
        acc_decision_tree = round(decision_tree.score(X, y) * 100, 2)
        decision_tree.fit(X, y)
        acc_decision_tree_r = round(decision_tree.score(X, y) * 100, 2)    

        # Random Forest
        random_forest = RandomForestClassifier(n_estimators=100)
        random_forest.fit(fake_X, fake_y)
        acc_random_forest = round(random_forest.score(X, y) * 100, 2)
        random_forest.fit(X, y)
        acc_random_forest_r = round(random_forest.score(X, y) * 100, 2)

        models = pd.DataFrame({
        'Model': [ 'KNN', 'Logistic Regression', 
                  'Random Forest', 'Naive Bayes', 'Perceptron', 
                  'Stochastic Gradient Decent', 'Linear SVC', 
                  'Decision Tree'],
        'Score_s_r': [ acc_knn, acc_log, 
                  acc_random_forest, acc_gaussian, acc_perceptron, 
                  acc_sgd, acc_linear_svc, acc_decision_tree],    
        'Score_r_r': [ acc_knn_r, acc_log_r, 
                  acc_random_forest_r, acc_gaussian_r, acc_perceptron_r, 
                  acc_sgd_r, acc_linear_svc_r, acc_decision_tree_r]})
           
        models['KPI'] = np.where(models['Score_s_r']>=models['Score_r_r']*0.80, 1, 0)#1:Satisfied
        models = models.sort_values(by='Score_s_r', ascending=False)
        #print(models)
        
        kpi_sum = models['KPI'].sum()
        if kpi_sum >= 4 :
            #print ("Satisfied "+str(kpi_sum)+" model")
            models.to_csv(directory+"eva_model_kpi"+str(e)+"_kpi80_"+str(kpi_sum)+".csv", header=True, index= None)
            kpi = "OK"
        else:
            print("BAD!BAD!") 
            kpi = "NO"
            os.remove(directory+'sample/synthetic_sample_'+str(e)+'.csv')
            os.remove(directory+'transform/synthetic_transform_'+str(e)+'.csv')
            os.remove(directory+'synthetic/synthetic_transform_rmhit'+str(e)+'.csv')
    
    return kpi
#     if DTA*100 > (DTA_r*100*0.9):
#         print("Satisfy the KPI!!")


#             DTA, DTA_r, _,_r = acc(directory,path,col_name,tar_col)
#             if (DTA*100 > (DTA_r*100*0.80)) & (_*100 > (_r*100*0.80)) :
#                 print(DTA,DTA_r,_,_r)
#                 print("Epoch: ",e," ,Satisfy the KPI!!")
#                 break
#             if (e == random_epoch[-1]):
#                 print("Sorry you have to re-generate!!")
#                 break
    