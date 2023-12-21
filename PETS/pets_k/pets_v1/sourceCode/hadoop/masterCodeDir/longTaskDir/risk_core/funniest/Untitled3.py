#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright 2017 Industrial Technology Research Institute

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 '''
from pyspark.context import SparkContext
#from pyspark.sql import HiveContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import regexp_replace
from pyspark.sql import Row
from pyspark.sql.functions import trim, date_format
from pyspark.sql.functions import lit
from pyspark.sql.functions import col,max
#from pyspark.sql.types import IntegerType, StringType,LongType,ArrayType
from pyspark.sql.types import *
from pyspark.sql.functions import udf
#from .udfItri import genDivInterval, isFailTcp, genNumInterval

import logging
from . import logging_setting
#from  .logging_tester
from .logging_tester import _getLogger


class HiveLibs(object):

	#建立hive溝通的sql content
	#sc = SparkContext()
	#sqlContext = HiveContext(sc)
	sqlContext = None
	join_=None
	_logger=None

	def __init__(self, SparkContext_):
        #sc = SparkContext()
		_logger=_getLogger(self.__class__.__name__)
		#self.sqlContext=HiveContext(SparkContext_)
		self.sqlContext = SQLContext(SparkContext_)
		self.join_ = self.Join()
		self.kChking=self.K()
		self.generalization=self.Generalization()
		self.dbOperation=self.DbOperation(self.sqlContext,_logger)
		#_logger=_getLogger(self.__class__.__name__)
		#print self.__class__.__name__
		#print __name__

	
##############################################################################
# join
##############################################################################
	class Join():
		
		def __init__(self):
				pass		

		#20170609
		def join2DF_removeDF1Duplication(self, df1, df2, cond,duplicationList, type):

			dfJoin = df1.join(df2, cond, type)#.drop(df_y.caseno).drop(df_y.seqno).drop(df_y.trackdate)
			cols = df1.columns
			if len(duplicationList) > 0:
				for colname in duplicationList:
					cols.remove(colname)
			for colname in df2.columns:
					cols.append(colname)
			dfJoin = dfJoin.select([col(column_) for column_ in cols])
			
			
			#dfJoin = df_y.join(kValueDF0420_, cond, 'right').drop(df_y.caseno)
			return dfJoin
			
		
		def join2DF_removeDF2Duplication(self, df1, df2, cond,duplicationList, type):

			dfJoin = df1.join(df2, cond, type)#.drop(df_y.caseno).drop(df_y.seqno).drop(df_y.trackdate)
			
			cols = df1.columns
			cols_= df2.columns
			if len(duplicationList) > 0:
				for colname in duplicationList:
					cols_.remove(colname)
			for colname in cols_:
					cols.append(colname)
			dfJoin = dfJoin.select([col(column_) for column_ in cols])
			
			#dfJoin = df_y.join(kValueDF0420_, cond, 'right').drop(df_y.caseno)

			return dfJoin

		#20170510
		#type 'left', 'inner', 'right', 'outer'
		def join2DF_WithType(self,df1, df2, cond, type):
			dfJoin = df1.join(df2, cond, type)#.drop(df_y.caseno).drop(df_y.seqno).drop(df_y.trackdate)
			#dfJoin = df_y.join(kValueDF0420_, cond, 'right').drop(df_y.caseno)
			list_1=""
			#list_2=[]
			for colName in cond:
				list_1='df2'+'.'+colName
				dfJoin=dfJoin.drop(col(list_1))
			return dfJoin
			
		#20170424, drop df2 redundency columns
		def join2DF(self,df1, df2, cond):
			dfJoin = df1.join(df2, cond, 'inner')#.drop(df_y.caseno).drop(df_y.seqno).drop(df_y.trackdate)
			#dfJoin = df_y.join(kValueDF0420_, cond, 'right').drop(df_y.caseno)
			list_1=""
			#list_2=[]
			for colName in cond:
				list_1='df2'+'.'+colName
				dfJoin=dfJoin.drop(col(list_1))
			return dfJoin


##############################################################################
# K-Anonymity 
##############################################################################
	class K():

		#def __init__(self, SparkContext_):
			#sc = SparkContext()
			#HiveLibs.__init__(SparkContext_)
		def __init__(self):
				pass
			
		def maskSmallKValue(self, list_, kValue,tb_name__ ):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select id_row_, '
			
			#idx = 1
			
			for col_name_ in list_:
				tmpStr = tmpStr+'\n'+'case'+'\n'+'when'
				tmpStr = tmpStr+ ' k_Value <'+ str(kValue)+'\n'+'then \n'
				tmpStr = tmpStr+'regexp_replace('+col_name_+', \'.\', \'*\')'
				tmpStr = tmpStr+ '\nelse \n'
				tmpStr = tmpStr+col_name_
				tmpStr = tmpStr+ '\nend as '+col_name_+',\n'
			
		  
			
			tmpStr = tmpStr+ 'k_Value \n'
			tmpStr = tmpStr+'from '+ tb_name__
			#tmpStr = tmpStr+ ' where k_Value <'+ str(kValue)
			
			
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			#for col_name_ in list_:
				#df_=df_.replace(['\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____
		#20170511
		def maskSmallKValue_NoRowId(self, key_col,mask_list_, kValue,tb_name__ ):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select '+key_col+', '
			
			#idx = 1
			
			for col_name_ in mask_list_:
				tmpStr = tmpStr+'\n'+'case'+'\n'+'when'
				tmpStr = tmpStr+ ' k_Value <'+ str(kValue)+'\n'+'then \n'
				tmpStr = tmpStr+'regexp_replace('+col_name_+', \'.\', \'*\')'
				tmpStr = tmpStr+ '\nelse \n'
				tmpStr = tmpStr+col_name_
				tmpStr = tmpStr+ '\nend as '+col_name_+',\n'
			
		  
			
			tmpStr = tmpStr+ 'k_Value \n'
			tmpStr = tmpStr+'from '+ tb_name__
			#tmpStr = tmpStr+ ' where k_Value <'+ str(kValue)
			
			
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			#for col_name_ in list_:
				#df_=df_.replace(['\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____
		
		#計算k值得函數
		#要處理的欄位list
		#例如，l=['caseno','transdate','seqno']

		def initialcomputKvalue(self,genIndDF_Table):
			#from pyspark.sql.functions import lit
			tmpStr="""
				   select *
				   from %s
				   """%(genIndDF_Table)
			#print tmpStr
			genIndDF=self.sqlContext.sql(tmpStr)
			
			newpdfDF = genIndDF.withColumn("aa", lit(1))
			return newpdfDF
		
		#20170424, list_ is column name list
		def computKvalue_usingDF(self,list_, df_):
			cols = []
			for col_ in list_:
				cols.append(col(col_))
			#cols.append(col("count").alias("k_Value"))
			kValueDF0420_= df_.groupby(cols).count()
			cols.append(col("count").alias("k_Value"))
			kValueDF0420_= kValueDF0420_.select(cols)
			
			return kValueDF0420_
			
		#20170929, list_ is column name list
		#df_除了包含groupby欄位,還有其他要distinct的欄位,例如id,可以包含多個欄位
		def computKvalue_distnctOtherCols_usingDF(self,list_, df_):
			cols = []
			for col_ in list_:
				cols.append(col(col_))
			#cols.append(col("count").alias("k_Value"))
			kValueDF0420_= df_.distinct().groupby(cols).count()
			cols.append(col("count").alias("k_Value"))
			kValueDF0929_= kValueDF0420_.select(cols)
			
			return kValueDF0929_
			
		#20170515
		def recyclelKValue_NoRowId_( self,list_, kValue,tb_name__ ):
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select '
			for col_name_ in list_:
				tmpStr = tmpStr+ col_name_+','
			tmpStr = tmpStr+'\n'+'case'+'\n'+'when '
			
			tmpStr__="""
				   (k_Value < %s) and
				   """%(kValue)
			
			tmpStr = tmpStr+tmpStr__
			idx = 1
			#print len(list_)
			tmpStr = tmpStr+'('
			for col_name_ in list_:
				
				if idx < len(list_):
					#print idx
					tmpStr = tmpStr+ col_name_+ '==\'\"NA\"\' or '
					#tmpStr = tmpStr+ col_name_+ '==\"NA\" or '
				else:
					tmpStr = tmpStr+ col_name_ +'==\'\"NA\"\''
					#tmpStr = tmpStr+ col_name_ +'==\"NA\"'
				idx=idx+1
			tmpStr = tmpStr+')\n'    
			tmpStr = tmpStr+ 'then 999 \n'
			tmpStr = tmpStr+ 'else k_Value \n'
			tmpStr = tmpStr+ 'end as k_Value \n'
			tmpStr = tmpStr+ 'from  '+tb_name__+'\n'
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)


			return df_

		def computKvalue_1(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
				
			tmpStr='\n'
			tmpStr = tmpStr+ 'select id_row_, '
			idx = 1
			
			#print list_
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ', sum(aa) over (partition by  '
			
			idx = 1
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ' order by id) as sum_k'
				 
			#tmpStr=tmpStr[0:len(tmpStr)]    
			tmpStr = tmpStr+' from '+ tb_name__
			#print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
			
			df____=df_


			return df____
		
		#20150511
		def computKvalue_1_NoRowId(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
				
			tmpStr='\n'
			tmpStr = tmpStr+ 'select  '
			idx = 1
			
			#print list_
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ', sum(aa) over (partition by  '
			
			idx = 1
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ' order by id) as sum_k'
				 
			#tmpStr=tmpStr[0:len(tmpStr)]    
			tmpStr = tmpStr+' from '+ tb_name__
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
			
			df____=df_


			return df____	

		
		#要處理的欄位list
		#例如，l=['caseno','transdate','seqno']
		def computKvalue_2(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select id_row_, '
			idx = 1
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ', sum_k,  \n'
			
			idx = 1
			tmpStr = tmpStr+ ' max(sum_k) over(partition by   '
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ' order by '+list_[0]+') as k_Value'
				 
			#tmpStr=tmpStr[0:len(tmpStr)]    
			tmpStr = tmpStr+' from '+ tb_name__
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____
		#20170511
		def computKvalue_2_NoRowId(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select  '
			idx = 1
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ', sum_k,  \n'
			
			idx = 1
			tmpStr = tmpStr+ ' max(sum_k) over(partition by   '
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ' order by '+list_[0]+') as k_Value'
				 
			#tmpStr=tmpStr[0:len(tmpStr)]    
			tmpStr = tmpStr+' from '+ tb_name__
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____

		#由計算好K值的table(如kValueDF__Table__)選出indirect欄位及一個sensitive欄位
		#並將indirect欄位及一個sensitive欄位放入list_，sensitive欄位放入最後一個位置
		def computLDiver__(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select id_row_, '
			idx = 1
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ', max(k_Value) over(partition by '  
			
				
			del list_[len(list_)-1]
			list_tmp = list_
			idx = 1
			
			for col_name_ in list_tmp:
				if(idx < len(list_tmp)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+' order by '+list_tmp[0]

			
			tmpStr = tmpStr+') as k_Value1 \n'
				 
			#tmpStr=tmpStr[0:len(tmpStr)]    
			tmpStr = tmpStr+' from '+ tb_name__
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____
		#20170511
		def computLDiver__NoRowId(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select  '
			idx = 1
			
			for col_name_ in list_:
				if(idx < len(list_)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ', max(k_Value) over(partition by '  
			
				
			del list_[len(list_)-1]
			list_tmp = list_
			idx = 1
			
			for col_name_ in list_tmp:
				if(idx < len(list_tmp)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+' order by '+list_tmp[0]

			
			tmpStr = tmpStr+') as k_Value1 \n'
				 
			#tmpStr=tmpStr[0:len(tmpStr)]    
			tmpStr = tmpStr+' from '+ tb_name__
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____	
			
		#由計算好K值的table(如kValueDF__Table__)選出indirect欄位及一個sensitive欄位
		#並將indirect欄位及一個sensitive欄位放入list_，sensitive欄位放入最後一個位置
		def computLDiverFinal(self,list_, tb_name__):
				
			#registerTempTable_forsparksql(df, "tb_name__")
			tmpStr='\n'
			tmpStr = tmpStr+ 'select '
			idx = 1
			
			sensitiveEm = list_[len(list_)-1]

			listMinusOne = list_
			
			del listMinusOne[len(listMinusOne)-1]
			for col_name_ in listMinusOne:
				if(idx < len(listMinusOne)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
			tmpStr = tmpStr+ ',count(distinct '+sensitiveEm+') as l_divers\n'  
			tmpStr = tmpStr+' from '+ tb_name__
			tmpStr = tmpStr+'\n group by '
			idx=1
			for col_name_ in listMinusOne:
				if(idx < len(listMinusOne)):
					#print list_.count(col_name_)
					tmpStr = tmpStr+col_name_+','
				else:
					tmpStr = tmpStr+col_name_
				idx = idx+1;
			
		 
			print (tmpStr)
			df_=self.sqlContext.sql(tmpStr)
			for col_name_ in list_:
				df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
		 
			df____=df_

			return df____


##############################################################################
# generalization
##############################################################################
	class Generalization():

			def generlizeUnixtimeColumn(self, selection, col_name_,tmp_tb_name_):
				selection = int(selection)
				tmpDF = self.getColumnWithRmQuatTrim(col_name_,tmp_tb_name_)
				self.registerTempTable_forsparksql(tmpDF, "tb_name__")
				
				tmpStr="q"
				if(selection ==2):
					tmpStr="""
						  select id_row_,
						  CONCAT_WS('_',year(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss')),month(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss'))) as %s 
						  from %s
						  """%(col_name_,col_name_,col_name_,"tb_name__")
						
				elif (selection ==1):
					tmpStr="""
						  select id_row_,
						  year(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss')) as %s 
						  from %s
						  """%(col_name_,col_name_,"tb_name__")
				elif(selection == 3):
					tmpStr="""
					   select id_row_,
					   date_format(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss'), 'yyyy-MM-dd') as %s 
					   from %s
					   """%(col_name_,col_name_,"tb_name__")
				else :
					print ('selection out of [1,2,3]')
					return

					
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				df____=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df____
			
			#20170511
			def generlizeUnixtimeColumn_NoRowId(self, selection, col_name_,tmp_tb_name_):
				selection = int(selection)
				tmpDF = self.getColumnWithRmQuatTrim(col_name_,tmp_tb_name_)
				self.registerTempTable_forsparksql(tmpDF, "tb_name__")
				
				tmpStr="q"
				if(selection ==2):
					tmpStr="""
						  select 
						  CONCAT_WS('_',year(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss')),month(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss'))) as %s 
						  from %s
						  """%(col_name_,col_name_,col_name_,"tb_name__")
						
				elif (selection ==1):
					tmpStr="""
						  select 
						  year(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss')) as %s 
						  from %s
						  """%(col_name_,col_name_,"tb_name__")
				elif(selection == 3):
					tmpStr="""
					   select 
					   date_format(from_unixtime(%s, 'yyyy-MM-dd HH:mm:ss'), 'yyyy-MM-dd') as %s 
					   from %s
					   """%(col_name_,col_name_,"tb_name__")
				else :
					print ('selection out of [1,2,3]')
					return

					
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				df____=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
				
				return df____
			

			#概化time stamp('yyyy-MM-dd HH:mm:ss)，
			#selection=1，只輸出year
			#selection=2，只輸出year-month
			#selection=3，只輸出year-moth-day
			def generlizeTimestampColumn(self, selection,col_name_,tmp_tb_name_):
				tmpDF = self.getColumnWithRmQuatTrim(col_name_,tmp_tb_name_)
				self.registerTempTable_forsparksql(tmpDF, "tb_name__")
				selection = int(selection)
				tmpStr="q"
				if(selection ==1):
					tmpStr="""
					   select id_row_,
					   year(%s) as %s 
					   from %s
					   """%(col_name_,col_name_,"tb_name__")
				
				elif (selection ==2):
					tmpStr="""
					   select id_row_,
					   CONCAT_WS('-',year(%s),month(%s)) as %s 
					   from %s
					   """%(col_name_,col_name_,col_name_,"tb_name__")
				#date_format('a', 'MM/dd/yyy')
				elif(selection == 3):
					tmpStr="""
					   select id_row_,
					   date_format(%s, 'yyyy-MM-dd') as %s 
					   from %s
					   """%(col_name_,col_name_,"tb_name__")
				else :
					print ('selection out of [1,2,3]')
					return
				   
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				#df____=df_.replace(['\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df_
			
			#20170511
			def generlizeTimestampColumn_NoRowId(self, selection,col_name_,tmp_tb_name_):
				tmpDF = self.getColumnWithRmQuatTrim(col_name_,tmp_tb_name_)
				self.registerTempTable_forsparksql(tmpDF, "tb_name__")
				selection = int(selection)
				tmpStr="q"
				if(selection ==1):
					tmpStr="""
					   select 
					   year(%s) as %s 
					   from %s
					   """%(col_name_,col_name_,"tb_name__")
				
				elif (selection ==2):
					tmpStr="""
					   select 
					   CONCAT_WS('-',year(%s),month(%s)) as %s 
					   from %s
					   """%(col_name_,col_name_,col_name_,"tb_name__")
				#date_format('a', 'MM/dd/yyy')
				elif(selection == 3):
					tmpStr="""
					   select 
					   date_format(%s, 'yyyy-MM-dd') as %s 
					   from %s
					   """%(col_name_,col_name_,"tb_name__")
				else :
					print ('selection out of [1,2,3]')
					return
				   
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)

				return df_

			#概化字串,String
			#pos，字串開始位置，由1開始
			def generlizeStringColumn(self, pos, length,col_name_,tmp_tb_name_):
				
				pos=int(pos)
				length=int(length)
				tmpDF = self.getColumnWithRmQuatTrim(col_name_,tmp_tb_name_)
				self.registerTempTable_forsparksql(tmpDF, "tb_name__")

				tmpStr="""
					   select id_row_,
					   substr( %s, %s,%s) as %s 
					   from %s
					   """%(col_name_,pos,length,col_name_,"tb_name__")
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				df____=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df____
				
			#20170511
			def generlizeStringColumn_NoRowId(self, pos, length,col_name_,tmp_tb_name_):
				
				pos=int(pos)
				length=int(length)
				tmpDF = self.getColumnWithRmQuatTrim(col_name_,tmp_tb_name_)
				self.registerTempTable_forsparksql(tmpDF, "tb_name__")

				tmpStr="""
					   select 
					   substr( %s, %s,%s) as %s 
					   from %s
					   """%(col_name_,pos,length,col_name_,"tb_name__")
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				df____=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df____

			#20170316
			#將數值型欄位(col_name_)，根據list ll，概化成數值區間
			#ll為區間分隔點的list，可由genDivInterval產生
			#col_name_欄位名稱，
			#tmp_tb_name_為table 名稱，由registerTempTable_forsparksql產生
			def generlizeNumColumn(min_, max_,ll,col_name_,tmp_tb_name_):
				
				idx =0
				tmpStr='array('
				for com in ll:
					if idx==len(ll)-1:
						tmpStr=tmpStr+str(com)+')'
					else:
						tmpStr=tmpStr+str(com)+','
					idx=idx+1
				print (tmpStr)
				
				
				tmpStr_="""
						select id_row_,
						genNumInterval_(%s,%s,%s,%s) as %s
						from %s
					   """%(min_,max_,col_name_,tmpStr,col_name_,tmp_tb_name_)
				print (tmpStr_)
				df_=sqlContext.sql(tmpStr_)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df_
				
				
			#20170511
			def generlizeNumColumn_NoRowId(min_, max_,ll,col_name_,tmp_tb_name_):
				
				idx =0
				tmpStr='array('
				for com in ll:
					if idx==len(ll)-1:
						tmpStr=tmpStr+str(com)+')'
					else:
						tmpStr=tmpStr+str(com)+','
					idx=idx+1
				print (tmpStr)
				
				
				tmpStr_="""
						select 
						genNumInterval_(%s,%s,%s,%s) as %s
						from %s
					   """%(min_,max_,col_name_,tmpStr,col_name_,tmp_tb_name_)
				print (tmpStr_)
				df_=sqlContext.sql(tmpStr_)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df_
				
			def getGenerlizeTimestamp(self, selection,col_name_):
				selection = int(selection)
				tmpStr="q"
				if(selection ==1):
					tmpStr="""
					   year(%s) as %s 
					   """%(col_name_,col_name_)
				
				elif (selection ==2):
					tmpStr="""
					   CONCAT_WS('-',year(%s),month(%s)) as %s 
						"""%(col_name_,col_name_,col_name_)
				#date_format('a', 'MM/dd/yyy')
				elif(selection == 3):
					tmpStr="""
					   date_format(%s, 'yyyy-MM-dd') as %s 
					   """%(col_name_,col_name_)
				else :
					print ('selection out of [1,2,3]')
					return
				   
				print (tmpStr)
				return tmpStr
			
		#20170515	
			def getGenerlizeTimestamp_usingUDF(self, selection,col_name_):
			
				pos=int(selection)
				#length=int(length)

				tmpStr="""
					   generlizeTimeStamp_( %s, %s) as %s 
					   """%(pos,col_name_,col_name_)
				print (tmpStr)
				return tmpStr
			
			
			def genNumInterval(self, inMin, inMax,intIn,ls):
				intMin = long(str(inMin))
				intMax = long(str(inMax))

				############################################################################################################
				#intInput = long(str(intIn))
				
				try:                                             
					intInput = long(str(intIn))
				except ValueError: 
					outTmp=''
					return 'null'
				#print "Something went wrong {!r}".format(x)
				
				
				lsLen = len(ls)
				outTmp='['
				idx=0
				#print ls
				for comp in ls:
					if(idx==0): 
						if(intInput < ls[idx] ):
							outTmp=outTmp+str(intMin)+', '+ str(ls[idx])+']'
							break
						if(intInput == ls[idx] ):
							outTmp=outTmp+str(intMin)+', ' +str(comp) +')'
							break
					if((ls[idx-1]<intInput) & (intInput<ls[idx])):
						outTmp=outTmp+str(ls[idx-1])+', ' +str(ls[idx])+']'
						break
					if((ls[idx-1]==intInput) & (intInput<ls[idx])):
						outTmp=outTmp+str(ls[idx-1])+', ' +str(ls[idx])+']'
						break
					if(idx==len(ls)-1):
						#print 'max'+ str(ls[idx])
						if(intInput > ls[idx] ):
							outTmp=outTmp+ str(ls[idx])+', '+ str(intMax)+']'
							break
						if(intInput == ls[idx] ):
							outTmp=outTmp+ str(ls[idx])+', ' +str(intMax)+']'
							break
					idx= idx+1
			 
				return outTmp;

			#20170316
			#將genNumInterval註冊為udf函數，udf函數定名為genNumInterval_
			#sqlContext.registerFunction("genNumInterval_", genNumInterval, StringType())

			#20170316
			#inMn, inMax分別為特定數值型欄位的minimum及maximum
			#依據inMin, inMax，以等分方式產生NumInterval個分隔點，輸出為list
			def genDivInterval(self, inMin, inMax,NumInterval):
				intMin = long(inMin)
				intMax = long(inMax)
				
				#print intMin
				#print intMax
				#print int(NumInterval)
				
				step = long((intMax-intMin)/long(NumInterval))
				#print 'Div step='+ str(step)
				#idx = 1
				ls=[step]
				tmp = step
				while((tmp )<inMax):
					ls.append(tmp)
					#idx=idx+1
					tmp=tmp+step
				#print ls    
				return ls
				
			#去除雙引號&trim，取代\N，na成NA，取代空值('')成NULL
			def getColumnWithRmQuatTrim(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select id_row_, %s as %s
					   from %s
					   """%(col_name_,col_name_,tmp_tb_name_)
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				
				ddf = df_.select(df_.id_row_, regexp_replace(col_name_,'(")','')).toDF('id_row_',col_name_)
				
				#df_Rdd = df_.rdd.map(lambda x: (x[0],x[1].replace("\"","")))
				
				#df__= sqlContext.createDataFrame(df_Rdd, ['id_row_', col_name_])
				#df___= df__.select(df__.id_row_,trim(col(col_name_))).toDF('id', col_name_)
				df____=ddf.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				return df____
			
			#20170511
			def getColumnWithRmQuatTrim_NoRowId(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select %s as %s
					   from %s
					   """%(col_name_,col_name_,tmp_tb_name_)
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				
				ddf = df_.select( regexp_replace(col_name_,'(")','')).toDF(col_name_)
				df____=ddf.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				return df____

			#選擇indirect columns，
			#去除雙引號&trim，取代\N，na成NA，取代空值('')成NULL
			def getIndirectColumns(self, list_,df):
				#print '20170522'
				list_.insert(0, 'id_row_')
				df_=df.select([col(column_).alias(column_) for column_ in list_])
				ddf = df_.select( [regexp_replace(column_,'(")','').alias(column_) for column_ in list_])
				for col_name_ in list_:
					ddf=ddf.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
				df____=ddf

				return df____
			#20170510
			def getIndirectColumns_NoPreprocess(self, list_,df):
				list_.insert(0, 'id_row_')
				df_=df.select([col(column_).alias(column_) for column_ in list_])
				#ddf = df_.select( [regexp_replace(column_,'(")','').alias(column_) for column_ in list_])
				ddf=df_
				for col_name_ in list_:
					#ddf=ddf.replace(['\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
					ddf=ddf.replace([r'"\\N"'],['"NA"'],col_name_).replace([r'"\N"'],['"NA"'],col_name_).replace(['"na"'],['"NA"'],col_name_).replace(['""'],['"NULL"'],col_name_)

				df____=ddf

				return df____
				
			#20170511
			def getIndirectColumns_NoRowId(self, list_,df):
				#list_.insert(0, 'id_row_')
				df_=df.select([col(column_).alias(column_) for column_ in list_])
				ddf = df_.select( [regexp_replace(column_,'(")','').alias(column_) for column_ in list_])
				for col_name_ in list_:
					ddf=ddf.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
				df____=ddf

				return df____
			#20170510
			def getIndirectColumns_NoPreprocess_NoRowId(self, list_,df):
				#list_.insert(0, 'id_row_')
				df_=df.select([col(column_).alias(column_) for column_ in list_])
				#ddf = df_.select( [regexp_replace(column_,'(")','').alias(column_) for column_ in list_])
				ddf=df_
				for col_name_ in list_:
					ddf=ddf.replace([r'"\\N"'],['"NA"'],col_name_).replace([r'"\N"'],['"NA"'],col_name_).replace(['"na"'],['"NA"'],col_name_).replace(['""'],['"NULL"'],col_name_)
				df____=ddf

				return df____	


			#generlized indirect columns
			def generlizedIndirectColumns(self, list_, ttb_name__):
				
				#ddf.registerTempTable( "ttb_name__")
					
				#tb = registerTempTable_forsparksql(df, "tb_name__")
				#print tb
				tmpStr='           \n'
				tmpStr = tmpStr+ '           select id_row_, '
				idx = 1
				for col_name_ in list_:
					if(idx < len(list_)):
						#print list_.count(col_name_)
						tmpStr = tmpStr+col_name_+','
					else:
						tmpStr = tmpStr+col_name_
					idx = idx+1;
					 
				#tmpStr=tmpStr[0:len(tmpStr)]    
				tmpStr = tmpStr+'from '+ ttb_name__+'\n'
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				
				for col_name_ in list_:
					df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				df____=df_


				return df____
			#20170511
			def generlizedIndirectColumns_NoRowId(self, list_, ttb_name__):
				
				#ddf.registerTempTable( "ttb_name__")
					
				#tb = registerTempTable_forsparksql(df, "tb_name__")
				#print tb
				tmpStr='           \n'
				tmpStr = tmpStr+ '           select '
				idx = 1
				for col_name_ in list_:
					if(idx < len(list_)):
						#print list_.count(col_name_)
						tmpStr = tmpStr+col_name_+','
					else:
						tmpStr = tmpStr+col_name_
					idx = idx+1;
					 
				#tmpStr=tmpStr[0:len(tmpStr)]    
				tmpStr = tmpStr+'from '+ ttb_name__+'\n'
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				
				for col_name_ in list_:
					df_=df_.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				df____=df_


				return df____	
				
			#20170501, adding Double Quotes#####
			#generlized indirect columns
			def paddingDoubleQuotesColumns(self, list_, ttb_name__):
				
				#ddf.registerTempTable( "ttb_name__")
					
				#tb = registerTempTable_forsparksql(df, "tb_name__")
				#print tb
				tmpStr='           \n'
				tmpStr = tmpStr+ '           select '
				idx = 1
				print (len(list_))
				for col_name_ in list_:
					if(idx < len(list_)):
						#print list_.count(col_name_)
						#print col_name_
						#print idx
						tmpStr = tmpStr+' padDoubleQuoyes_('+col_name_+') as '+col_name_+','
						
					else:
						tmpStr = tmpStr+' padDoubleQuoyes_('+col_name_+') as '+col_name_
					idx = idx+1
					 
				#tmpStr=tmpStr[0:len(tmpStr)]    
				tmpStr = tmpStr+' from '+ ttb_name__+'\n'
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				
				#for col_name_ in list_:
					#df_=df_.replace(['\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)

				df____=df_


				return df____
				

			def generlizeIPColumn(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select id_row_,
					   case
					   when size(split( %s, '[\.]')) ==4 
					   then
					   CONCAT_WS('.',split( %s, '[\.]')[0],split( %s, '[\.]')[1],'*','*')
					   else
					   %s
					   end as %s
					   from %s
					   """%(col_name_,col_name_,col_name_,col_name_,col_name_,tmp_tb_name_)
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df_
			#20170511
			def generlizeIPColumn_NoRowId(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select 
					   case
					   when size(split( %s, '[\.]')) ==4 
					   then
					   CONCAT_WS('.',split( %s, '[\.]')[0],split( %s, '[\.]')[1],'*','*')
					   else
					   %s
					   end as %s
					   from %s
					   """%(col_name_,col_name_,col_name_,col_name_,col_name_,tmp_tb_name_)
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df_



			#20170512	
			def getGenerlizeString(self, pos, length,col_name_):
				
				pos=int(pos)
				length=int(length)

				tmpStr="""
					   generlizeString_( %s, %s,%s) as %s 
					   """%(pos,length,col_name_,col_name_)
				print (tmpStr)
				return tmpStr
				
			#20170512
			def getFilterNonNumberChar(self, col_name_):
				

				tmpStr="""
					   filterNonNumberChar_( %s) as %s 
					   """%(col_name_,col_name_)
				print (tmpStr)
				return tmpStr
			
			def getFilterNonNumberInt(self, col_name_):
				tmpStr="""
						filterNonNumberInt_( %s) as %s 
						"""%(col_name_,col_name_)
				print (tmpStr)
				return tmpStr
				
			#20170714, tony	
			def getNogenerlizeInt(self, col_name_):
				tmpStr="""
						getNogenerlizeInt_( %s) as %s
						"""%(col_name_,col_name_)
				print (tmpStr)
				return tmpStr

			def getNogenerlize(self, col_name_):
				
			
				tmpStr="""
					   %s 
					   """%col_name_
				print (tmpStr)
				return tmpStr
			
			#20170713
			def getGenerlizeCountry(self, col_name_, rule):
			
				idx =0
				tmpStr='array('
				for com in rule:
					if idx==len(rule)-1:
						tmpStr=tmpStr+'"'+str(com)+'")'
					else:
						tmpStr=tmpStr+'"'+str(com)+'",'
					idx=idx+1
				
				tmpStr_ = """
					generalizeCountry_( %s, %s) as %s
					"""%(col_name_, tmpStr, col_name_)
				print (tmpStr_)
				return tmpStr_
			#20170713
			def getGenerlizeAddress(self, num, col_name_):
				num = int(num)
				tmpStr = """
						generlizeAddress_( %s, %s) as %s
						"""%(num, col_name_, col_name_)
				print (tmpStr)
				return tmpStr
							
			#20170512
			def generlizeString(self, pos, length,inputStr):
				inputStr=str(inputStr)
				pos=int(pos)
				length=int(length)
				if(length > len(inputStr)):
					length = len(inputStr)
				return inputStr[pos: length]

			#percentile是hive的agreegate function, 有數量限制,用dpkts這欄位去跑,會當掉
			#雖然spark sql叫的到hive function,但hive udaf可能會因memory當掉,hive udf則沒問題
			def getColumnQPercentile(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select dpkts,
					   case
					   when  cast(%s as BIGINT) > 0
					   then
						%s
					   else
					   0
					   end as tmpCol
					   from %s
					   """%(col_name_,col_name_,tmp_tb_name_)
				
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				df_.registerTempTable("tmpTb")
				
				tmpStr="""
					   select 
					   percentile(cast(tmpCol as BIGINT),array(0.25,0.5,0.75) ) 
					   from tmpTb
					   """
				
				
				#print tmpStr
				df__=self.sqlContext.sql(tmpStr)
				
				
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df__

			#df_=sqlContext.sql('select percentile(cast(count__ as BIGINT),1 ) from pdfDFTable__')
			#           percentile(cast(%s as BIGINT),array(0.25,0.5,0.75) ) 


			#20170418, get element which count_ smaller than n
			def getOutlierList(self, col_name_,tmp_tb_name_, n):
				
				count_value=int(n)
				df = self.getColumnDistribution(col_name_,tmp_tb_name_)
				tmpTable = self.registerTempTable_forsparksql(df, "tmpTABLE")
				
				tmpStr="""
					   select %s as %s
					   from %s
					   where count__ < %s
					   """%(col_name_,"tmpcol_name_",tmpTable,count_value )
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				
				ddf = df_.select( regexp_replace("tmpcol_name_",'(")','')).toDF("tmpcol_name_")

				#df_ = df.select(col_name_).filter(col("count__") < count_value)
				df__=ddf.replace([r'\N'],['NA'],col_name_).replace(['na'],['NA'],col_name_).replace([''],['NULL'],col_name_)
				
				#the following x represents each row of df__
				return df__.rdd.map(lambda x: x.tmpcol_name_).collect()


			#20170316
			#產生概化數值型欄位(col_name_)的SQL語法
			def geGerlizeNumComm(self, min_, max_,ll,col_name_):
				
				idx =0
				tmpStr='array('
				for com in ll:
					if idx==len(ll)-1:
						tmpStr=tmpStr+str(com)+')'
					else:
						tmpStr=tmpStr+str(com)+','
					idx=idx+1
				#print tmpStr
				
				
				tmpStr_="""
						genNumInterval_(%s,%s,%s,%s) as %s
					   """%(min_,max_,col_name_,tmpStr,col_name_)
				#print tmpStr_
				#df_=sqlContext.sql(tmpStr_)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return tmpStr_
				
				#20170419
			#產生概化outlier欄位(col_name_)的SQL語法
			def geGerlizeOutlierCol(self, outlierList,toValue,col_name_):
				
				idx =0
				tmpStr='array('
				for com in outlierList:
					if idx==len(outlierList)-1:
						try:
							tmpStr=tmpStr+'"'+str(com)+'")'
						except UnicodeEncodeError:
							tmpStr=tmpStr+'"'+str(com.encode('utf-8'))+'")'
					else:
						try:
							tmpStr=tmpStr+'"'+str(com)+'",'
						except UnicodeEncodeError:
							tmpStr=tmpStr+'"'+str(com.encode('utf-8'))+'",'
							
					idx=idx+1
				#print tmpStr
				
				try:			
					tmpStr_="""
							outlierGener_(%s,\"%s\",%s) as %s
						   """%(tmpStr,toValue,col_name_,col_name_)
				except UnicodeDecodeError:
					tmpStr_="""
							outlierGener_(%s,\"%s\",%s) as %s
						   """%(tmpStr,toValue.encode('utf-8'),col_name_,col_name_)			
				#print tmpStr_
				#df_=sqlContext.sql(tmpStr_)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return tmpStr_
		

##############################################################################
# dbOperation 
##############################################################################
	class DbOperation(object):
			sqlContext=None
		
			def __init__(self, sqlContext_, _logger_):
				#print "DbOperation __init__"
				self.sqlContext=sqlContext_
				self._logger=_logger_

			def get_sqlContext(self):
				return self.sqlContext
			

			#20170424, drop df2 redundency columns
			#20170610, drop df2 redundency columns
			def dropForDF(self,df1, duplicationList):
				cols= df1.columns
				for colname in duplicationList:
						cols.remove(colname)
				
				dfDrop= df1.select([col(column_) for column_ in cols])
				
				return dfDrop
				

				

			#CSVPath for hdfs
			def loadDFFromCSVWithHeader(self, CSVPath):
				df = self.sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true').load(CSVPath)
				return df

			def loadDFFromCSVWithNoHeader(self, CSVPath,customSchema):
				#customSchema_ = json.loads(customSchema)
				#customSchema_ = StructType(customSchema)
				df = self.sqlContext.read \
				.format('com.databricks.spark.csv') \
				.options(header='true') \
				.load(CSVPath, schema = customSchema)

				
			#20170416, 20170510 add mode("overwrite"
			#註冊暫時table nama，用於spark sql
			def registerRealHiveTable_forsparksql(self,data_frame_, tb_name_):
				data_frame_.write.format("orc").mode("overwrite").saveAsTable(tb_name_)
				return tb_name_

			def dropRealHiveTable_forsparksql(self,tmp_tb_name_):
				tmpStr="""
					   drop table if exists %s
					   """%tmp_tb_name_
				#print tmpStr
				self.sqlContext.sql(tmpStr)
				return 		
				
			
			def registerFunctions(self,genDivInterval,isFailTcp,genNumInterval,outlierGener,padDoubleQuoyes):
			
				self.sqlContext.registerFunction("genDivInterval_", genDivInterval, ArrayType(LongType()))
				self.sqlContext.registerFunction("isFailTcp_", isFailTcp, IntegerType())
				self.sqlContext.registerFunction("genNumInterval_", genNumInterval, StringType())
				self.sqlContext.registerFunction("outlierGener_", outlierGener, StringType())
				self.sqlContext.registerFunction("padDoubleQuoyes_", padDoubleQuoyes, StringType())  
				
				funsDF = self.sqlContext.sql("show functions")
				print (len(funsDF.collect()))

					

			
			#顯示hive所有DB
			def show_databases(self):
				#"substitute for `show databases`"
				self._logger.debug("spak executed hive sql:%s" % ("show databases"))
				#_logger.info("the function execute:%s" % ("show databases"))
				return self.sqlContext.sql("show databases").show()
				
					
			#使用hive特定DB，並顯示DB所有table name
			def use_databases(self, db_name_):
				#print "use_databases ======"
				self._logger.debug("spark executed hive sql:%s" % ("use databases"))
				db_name='use {}'
				self.sqlContext.sql(db_name.format(db_name_))
				return self.sqlContext.sql("show tables").show()
				
			#顯示table schema
			def print_schema(self, tb_name_):
				
				db_name='select * from {}'
				df_twren=self.sqlContext.sql(db_name.format(tb_name_))
				df_twren = df_twren.withColumn("id_row_", monotonically_increasing_id())
				df_twren.printSchema()
				return df_twren
			#20170511
			def print_schema_NoRowId(self, tb_name_):
				
				db_name='select * from {}'
				df_twren=self.sqlContext.sql(db_name.format(tb_name_))
				#df_twren = df_twren.withColumn("id_row_", monotonically_increasing_id())
				df_twren.printSchema()
				return df_twren

			#註冊暫時table nama，用於spark sql
			def registerTempTable_forsparksql(self, data_frame_, tb_name_):
				data_frame_.registerTempTable(tb_name_)
				return tb_name_
			#計算資料總列數
			def getCount(self, tmp_tb_name_):
				tmpStr="""
					   select count(*) counts_
					   from %s
					   """%tmp_tb_name_
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				#countRdd = df_.rdd.map(lambda p: p.counts_)
				
				#return countRdd.take(1)
				list_=df_.take(1)
				return list_[0].counts_


			###################################


			def getColumn(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select id_row_, %s as %s
					   from %s
					   """%(col_name_,col_name_,tmp_tb_name_)
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				
				return df_
				
			#20170511
			def getColumn_NoRowId(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select  %s as %s
					   from %s
					   """%(col_name_,col_name_,tmp_tb_name_)
				#print tmpStr
				df_=self.sqlContext.sql(tmpStr)
				return df_	




			def getColumnDistribution(self, col_name_,tmp_tb_name_):
				tmpStr="""
					   select %s as %s, count(*) as count__
					   from %s
					   group by %s
					   ORDER BY count__
					   """%(col_name_,col_name_,tmp_tb_name_,col_name_ )
				print (tmpStr)
				df_=self.sqlContext.sql(tmpStr)
				#coltRdd = df_.map(lambda p: p.col_name__)
				#return coltRdd
				return df_

				
			#20170510
			#CSVPath is a hdfs direct name 
			def dfToCSV(self, df, CSVPath,delimiter_):
				df.select('*').repartition(1).write.format('com.databricks.spark.csv')\
				.options(header='true', quoteMode='NONE',  escape='\'', delimiter=delimiter_).mode("overwrite").save(CSVPath)
				
			#20170531
			#CSVPath is a hdfs direct name 
			def dfToCSV_csvWithHeader_ForAdding_DoubleQuote(self, df, CSVPath,delimiter_):
				df.select('*').repartition(1).write.format('com.databricks.spark.csv')\
				.options(header='true', inferschema='false', quote='"', quoteMode='ALL', delimiter=delimiter_).mode("overwrite").save(CSVPath)
				#df_ = self.loadDFFromCSVWithHeader(CSVPath,delimiter_)
				#df_.select('*').repartition(1).write.format('com.databricks.spark.csv')\
				#.options(header='true', inferschema='false', quote='"', delimiter=',').mode("overwrite").save(CSVPath)
				####################

			#20170531
			#CSVPath is a hdfs direct name 
			def dfToCSV_csvWithNoHeader_ForAdding_DoubleQuote(self, df, CSVPath,customSchema,delimiter_):
				df__=self.loadDFFromCSVWithNoHeader(CSVPath,customSchema,delimiter_)
				df__.select('*').repartition(1).write.format('com.databricks.spark.csv')\
				.options(header='true', inferschema='false', quote='"', quoteMode='ALL',delimiter=',').mode("overwrite").save(CSVPath)
				#df_ = self.loadDFFromCSVWithHeader(CSVPath,delimiter_)
				#self.dfToCSV(df_, CSVPath,delimiter_)
				####################
			
			#CSVPath for hdfs dir name or file name
			def loadDFFromCSVWithHeader(self, CSVPath,delimiter_):
				##databrics bug,  adding option quote="'" (or quote="\'"), but output as "2008"
				df = self.sqlContext.read.format('com.databricks.spark.csv')\
				.options(header='true', inferschema='true', quote="\'", escape='\'', delimiter=delimiter_ )\
				.load(CSVPath)
				
				s = df.columns
				#更改DF的column名，這裡是去除'"'，不去除無法輸出成table
				df=df.select([col(column_).alias(column_.strip( '"' )) for column_ in s])
				return df

			def loadDFFromCSVWithNoHeader(self,CSVPath,customSchema,delimiter_):
				#customSchema_ = json.loads(customSchema)
				#customSchema_ = StructType(customSchema)
				#databrics bug,  adding option quote="'" (or quote="\'"), but output as "2008"
				df = self.sqlContext.read\
				.format('com.databricks.spark.csv')\
				.options(header='true', inferschema='true', quote="\'", escape='\'', delimiter=delimiter_)\
				.load(CSVPath, schema = customSchema)
				
				#df = df.withColumn("id_row_", monotonically_increasing_id())

				return df


			#20170416
			def createDFSchema__(self,col_name_list,colTyeList):
				customSchemall = []
				#customSchema=StructField
				ii=0
				len_ = len(col_name_list)
				len__ = len(col_name_list)
				if len_ != len__:
					print ('input list error')
					return customSchemall
				
				#customSchema = customSchema+'StructType(['
				for colName in col_name_list:
					
					 
					if colTyeList[ii] == 'int':
						customType=IntegerType()
					elif colTyeList[ii] == 'str':
						customType=StringType()
					elif colTyeList[ii] == 'long':
						customType=LongType()
						
					customSchema=StructField(colName,  customType, True)   

					customSchemall.append(customSchema)
					
				return StructType(customSchemall)

#(end for HiveLibs)		



if __name__ == '__main__':
	# In[14]:

	#20170316
	#genDivInterval的例子
	#min=20, max=18565311,
	#產生100個分隔點，輸出成list (ll)
	ll = genDivInterval(20, 18565311,100)
	print (ll)
	print (ll[0])
	genNumInterval(1, 18565311,1000, ll)
	#print geGerlizeNumComm(1, 18565311,ll,'count__','pdfDF_Table_')


	# In[27]:

	#20170316
	#genDivInterval的例子
	#用於generlizedIndirectColumns(步驟7)
	ll = genDivInterval(20, 18565311,100)
	print (geGerlizeNumComm(1, 18565311,ll,'count__'))


	# In[16]:

	#show all dataases
	print ('1. show all dataases')
	show_databases()

	#use databases
	print ('2. use dataases')
	use_databases("a_lvr_land")

	#print a table schema and get a dataframe for the table
	print ('3. show a table schema and get a dataframe for the table')
	df = print_schema("criminaldate_real")


	print ('4. register a temp table name for df, for spark sql')
	tmpTable = registerTempTable_forsparksql(df, "criminaldateTable__")
	print (tmpTable)

	print ('5. 取得特定欄位(caseno)概化後分布情形')
	genStrDf = generlizeStringColumn(1,5,"caseno","criminaldateTable__")


	# In[17]:

	#20170316
	#使用getColumnWithRmQuatTrim將seqno去除'"'
	#計算min 及 max
	pdfDF = getColumnWithRmQuatTrim("seqno",'criminaldateTable__') 
	pdfDF.describe().show()


	# In[18]:

	#20170316
	#generlizeNumColumn的例子
	changedTypedf = pdfDF.withColumn("seqno_", pdfDF["seqno"].cast(LongType()))
	#changedTypedf.printSchema()
	#changedTypedf.describe().show()
	#changedTypedf.select('seqno_')
	#20170316
	#產生分隔點list
	#註冊暫時table name
	#概化'seqno_'欄位
	ll = genDivInterval(237, 103123193751,10)
	changedTypedf.registerTempTable("changedTypedf_Table_")
	changedTypedf = generlizeNumColumn(237, 103123193751,ll,'seqno_','changedTypedf_Table_')
	#changedTypedf.show()


	# In[19]:

	changedTypedf.take(50)


	# In[29]:

	changedTypedf.registerTempTable("changedTypedf_Table_")
	changedTypedf = generlizeNumColumn(237, 103123193751,ll,'seqno_','changedTypedf_Table_')
	changedTypedf.select('seqno','seqno_').show()


	# In[20]:

	print ('6. 建立間接識別欄位資料結構')

	l=['caseno','trackdate','seqno']

	dd_ = getIndirectColumns(l,df)
	dd_.show(5)


	# In[28]:

	#20170316,
	#getGenerlizeString, getGenerlizeTimestamp, getGenerlizeTimestamp的例子
	print ('7. 針對間接識別欄位，指定概化函數，並進行概化')

	dd_.registerTempTable( "dd_Table__")
	#s = [getGenerlizeString(1,5,"caseno"),getGenerlizeTimestamp(3,"trackdate"),getGenerlizeString(1,5,"seqno") ]
	s = [getGenerlizeString(1,5,"caseno"),getGenerlizeTimestamp(3,"trackdate"),geGerlizeNumComm(237, 103123193751,ll,"seqno") ]

	genIndDF=generlizedIndirectColumns(s, "dd_Table__")
	genIndDF.show(5)

