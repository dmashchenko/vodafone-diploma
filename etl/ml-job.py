import os
import pickle
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
import configparser
import sys
import numpy as np
from pyspark.sql.functions import lit, udf, col, array
from pyspark.sql.types import FloatType, StringType

sys.path.append('ml/src')

model = pickle.load(open("out/traffic_predictor.pickle", "rb"))

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.aws/credentials"))
access_id = config.get("default", "aws_access_key_id")
access_key = config.get("default", "aws_secret_access_key")
access_token = config.get("default", "aws_session_token")
sc = SparkContext.getOrCreate()
log4jLogger = sc._jvm.org.apache.log4j
LOGGER = log4jLogger.LogManager.getLogger(__name__)
hadoop_conf = sc._jsc.hadoopConfiguration()
# hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
# hadoop_conf.set("fs.hdfs.impl", "org.apache.hadoop.hdfs.DistributedFileSystem")
hadoop_conf.set("fs.s3a.access.key", access_id)
hadoop_conf.set("fs.s3a.secret.key", access_key)
hadoop_conf.set("fs.s3a.session.token", access_token)

spark = SparkSession.builder.appName("ml-job") \
    .config("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider") \
    .getOrCreate()

jdbcurl = "jdbc:mysql://{0}:{1}/{2}?user={3}&password={4}".format(sys.argv[1], 3306, 'traffic', 'admin', 'admin1234')

columns = ["loc_lat", "loc_lon"]
features = {"traff_m1", "traff_m2", "traff_m3", "traff_m4", "traff_m5"}
columns.extend(features)

s3df = spark.read.option("header", True).csv("s3a://s3-storage-dmashchenko/dataset").select(columns)


@udf(returnType=FloatType())
def predict(arr):
    # model.predict() todo
    return float(arr[0]) + float(arr[1])


predictiondf = s3df.limit(5) \
    .withColumnRenamed("loc_lat", "lat") \
    .withColumnRenamed("loc_lon", "lon") \
    .withColumn("value", predict(array(features))) \
    .select("lon", "lat", "value") \
    .withColumn("month", lit("2020-07-01"))

predictiondf.show()

predictiondf.write.mode("append").jdbc(jdbcurl, table='traffic_prediction',
                                       properties={"driver": 'com.mysql.cj.jdbc.Driver'})

resultdf = spark.read.jdbc(jdbcurl, table='traffic_prediction', properties={"driver": 'com.mysql.cj.jdbc.Driver'})

resultdf.show()

spark.stop()
