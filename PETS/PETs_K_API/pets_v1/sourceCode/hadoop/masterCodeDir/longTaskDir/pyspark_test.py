from pyspark import SparkConf, SparkContext
#from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from funniest import HiveLibs

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorIndexer, FeatureHasher
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, DecisionTreeClassifier, LinearSVC
from xgboost import XGBClassifier
from pyspark.ml.classification import GBTClassifier
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

# load data file.
#inputData = spark_.read.format("libsvm").load("file:///home/hadoop/proj_/longTaskDir/pyspark_ML_test.txt")
#inputData = spark_.read.options(header="true").csv("file:///home/hadoop/proj_/data/output/t1/g_mac_t1_k_job1/g_mac_t1_k_job1.csv")
inputData = spark_.read.options(header="true").csv("file:///home/hadoop/proj_/data/input/t1/mac_t1/mac_t1.csv")
#inputData = sqlContext.read.format('com.databricks.spark.csv').options(header="true").load("file:///home/hadoop/proj_/longTaskDir/pyspark_ML_test.txt")

inputData_dropID = inputData.drop('id')
inputData_dropIDna = inputData_dropID.na.drop()

targetCol = ['race'] #sex
cols = inputData_dropIDna.columns
cols.remove(targetCol[0])

featureHasher = FeatureHasher(inputCols=cols, outputCol="features")
labelIndexer = StringIndexer(inputCol=targetCol[0], outputCol="label").fit(inputData_dropIDna)

# instantiate the base classifier.
lr = LogisticRegression(maxIter=10, tol=1E-6, labelCol="label", featuresCol="features")

# Gradient-boosted tree classifier
gbt = GBTClassifier(labelCol="label", featuresCol="features", maxIter=10)

xgb = XGBClassifier(nthread=-1)

rf = RandomForestClassifier(labelCol="label", featuresCol="features", numTrees=10)

dt = DecisionTreeClassifier(labelCol="label", featuresCol="features")

lsvc = LinearSVC(maxIter=10, regParam=0.1)

# generate the train/test split.
(train, test) = inputData_dropIDna.randomSplit([0.8, 0.2])

pipeline = Pipeline(stages=[labelIndexer, featureHasher, gbt])

# Train model.  This also runs the indexers.
model = pipeline.fit(train)

# Make predictions.
predictions = model.transform(test)

# obtain evaluator.
evaluator = MulticlassClassificationEvaluator(metricName="accuracy")

# compute the classification error on test data.
accuracy = evaluator.evaluate(predictions)
print("-------- Accuracy = %g --------" % (accuracy))
print("-------- Test Error = %g --------" % (1.0 - accuracy))
