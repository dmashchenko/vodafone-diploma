import os
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
import configparser

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
df = spark.read.option("header", True).csv("s3a://s3-storage-dmashchenko/dataset")
df.select('target').limit(10).show()
spark.stop()
