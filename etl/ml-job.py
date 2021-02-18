import os
import pickle
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
import configparser
import pandas as pd
import sys
import numpy as np

sys.path.append('ml/src')


def cast_to_float32(df):
    for c in df.columns:
        df[c] = df[c].astype(np.float32)


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

host = sys.argv[1]

jdbcurl = "jdbc:mysql://{0}:{1}/{2}?user={3}&password={4}".format(host, 3306, 'base_station', 'admin', 'admin1234')

dbdf = spark.read.jdbc(jdbcurl, table='traffic', properties={"driver": 'com.mysql.cj.jdbc.Driver'})

dbdf.show()

df = spark.read.option("header", True).csv("s3a://s3-storage-dmashchenko/dataset")
df.select('target', 'traff_m1', 'traff_m2').limit(5).show()
pdf = df.limit(5).toPandas()
cast_to_float32(pdf)
pdf.set_index('abon_id', inplace=True)
print(pdf.columns)
print(pdf.shape)
print(pdf[['traff_m1', 'traff_m2', 'traff_m3', 'traff_m4', 'traff_m5']].shape)
# print(model.predict(pdf[['traff_m1', 'traff_m2', 'traff_m3', 'traff_m4', 'traff_m5']]))
spark.stop()
