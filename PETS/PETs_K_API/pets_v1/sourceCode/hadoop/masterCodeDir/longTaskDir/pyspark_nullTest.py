from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from funniest import HiveLibs

from pyspark.ml.feature import StringIndexer, FeatureHasher
from pyspark.ml.classification import LogisticRegression, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

global sc, hiveLibs, sqlContext, spark_

# spark setting
appName = 'MLutility'
master_ = 'yarn'
warehouse_location = "hdfs://nodemaster:9000/user/hive/warehouse"

spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).config("spark.sql.warehouse.dir", warehouse_location).getOrCreate()

sc_ = spark_.sparkContext
sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

hiveLibs = HiveLibs(sc_)
sqlContext = hiveLibs.dbOperation.get_sqlContext()

inputData = spark_.read.options(header="true").csv("file:///home/hadoop/proj_/data/output/medical_drugs/g_privacy_medical_drugs_data_k_job1.csv")
print('---len raw---'+str(inputData.count()))

inputData_dropID = inputData.drop('Name')
inputData_dropIDna = inputData_dropID.na.drop(how='any')

print('---len drop na---'+str(inputData_dropIDna.count()))
print(inputData_dropIDna.show(10))