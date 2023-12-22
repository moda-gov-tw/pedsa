#from markdown import markdown
#from pyspark.context import SparkContext
#from pyspark.sql import HiveContext
#from pyspark.sql.types import IntegerType, StringType,LongType,ArrayType
from .Untitled3 import HiveLibs
#from .Untitled3 import other
#from .Untitled3 import HiveLibs.Join
#import logging
#from logging_tester import _getLogger

#_logger = logging.getLogger(__name__)

def joke():
    print 'joke'
					
#def registerFunctions(sc):
	
#	try:
#		sqlContext = HiveContext(sc)
#		sqlContext.registerFunction("genDivInterval_", genDivInterval, ArrayType(LongType()))
#		sqlContext.registerFunction("isFailTcp_", isFailTcp, IntegerType())
#		sqlContext.registerFunction("genNumInterval_", genNumInterval, StringType())
#		funsDF = sqlContext.sql("show functions")
#		functionList = funsDF.collect()
#		print len(functionList)
#		return sqlContext
#	except Exception as e:
		#logging.error(traceback.format_exc())
#		logging.error(e.message)
#		print e.message

