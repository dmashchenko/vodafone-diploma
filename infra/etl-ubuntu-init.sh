sudo apt-get update
sudo apt-get install -y python3-pip
yes Y| sudo apt install openjdk-11-jre-headless
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
wget --trust-server-names "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=spark/spark-3.0.1/spark-3.0.1-bin-hadoop3.2.tgz"
tar -xzf spark-3.0.1-bin-hadoop3.2.tgz
export SPARK_HOME=/home/ubuntu/spark-3.0.1-bin-hadoop3.2
export PYSPARK_PYTHON=python3
spark-3.0.1-bin-hadoop3.2/sbin/start-master.sh