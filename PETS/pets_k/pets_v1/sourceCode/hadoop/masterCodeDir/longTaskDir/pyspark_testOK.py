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

# load data file.
#inputData = spark_.read.format("libsvm").load("file:///home/hadoop/proj_/longTaskDir/pyspark_ML_test.txt")
inputData = spark_.read.options(header="true").csv("file:///home/hadoop/proj_/data/output/t1/g_mac_t1_k_job1/g_mac_t1_k_job1.csv")
#inputData = spark_.read.options(header="true").csv("file:///home/hadoop/proj_/data/output/medical_drugs/g_privacy_medical_drugs_data_k_job1.csv")
#inputData = sqlContext.read.format('com.databricks.spark.csv').options(header="true").load("file:///home/hadoop/proj_/longTaskDir/pyspark_ML_test.txt")
print(inputData.show(10))

ID = 'id' #'Name'
inputData_dropID = inputData.drop(ID)
print(inputData_dropID.show(10))

targetCol = ['education','race'] #'marital_status', 'education', 'country',  #['Gender', 'Education', 'manufacturer_country']

for col in targetCol:
    cols = inputData_dropID.columns
    cols.remove(col)

    print('all : '+str(inputData_dropID.columns))
    print('target : '+col)
    print('fetures : '+str(cols))

    hasher_feature = FeatureHasher(inputCols=cols, outputCol="features")
    featurized_data = hasher_feature.transform(inputData_dropID)

    indexer = StringIndexer(inputCol=col, outputCol="label")
    data = indexer.fit(featurized_data).transform(featurized_data)
    data.show(5)

    # generate the train/test split.
    (train, test) = data.randomSplit([0.8, 0.2])
    print('--------train--------')
    print(train.show(5))
    print('--------test--------')
    print(test.show(5))

    # instantiate the base classifier.
    lr = LogisticRegression(maxIter=10, tol=1E-6)#, fitIntercept=True)
    lr.setLabelCol('label').setFeaturesCol('features')

    # instantiate the One Vs Rest Classifier.
    ovr = OneVsRest(classifier=lr)

    # train the multiclass model.
    ovrModel = ovr.fit(train)

    # score the model on test data.
    predictions = ovrModel.transform(test)

    # obtain evaluator.
    evaluator = MulticlassClassificationEvaluator(metricName="accuracy")

    # compute the classification error on test data.
    accuracy = evaluator.evaluate(predictions)
    print("-------- {} --------".format(col))
    print("-------- Predict Accuracy = %g --------" % (accuracy))
    print("-------- Test Error = %g --------" % (1.0 - accuracy))