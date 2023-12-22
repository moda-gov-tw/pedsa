import pandas as pd
import numpy as np

DF = pd.read_csv('data/adult.csv',header=0)
row,_ = DF.shape
print(row)

DF['ONE_attribute'] = 'one'
DF['ID_'] = np.arange(0,row )
DF["nothing"] = ""
DF["naN"] = np.nan
DF.to_csv('data/adult_custom.csv',index=False)
print(DF.head(2))
