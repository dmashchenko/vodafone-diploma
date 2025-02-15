PYTHON = python3
export SPARK_HOME=/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/pyspark
export PYSPARK_PYTHON=python3

$(eval APP-IP :=  $(shell cd infra; terraform output app_ip))
$(eval ETL-IP :=  $(shell cd infra; terraform output etl_ip))
$(eval WAREHOUSE-HOST :=  $(shell cd infra; terraform output warehouse_host))

project-init:
	(cd ml/src; pwd; python3 -c "from data import preprocessor; preprocessor.load_raw_data_and_make_memory_optimized_dumps()")

app-init-infra-config:
	echo \[default\] > app/infra.cfg
	(cd infra; terraform output) >> app/infra.cfg

app-package-deploy: app-init-infra-config
	mkdir -p out
	zip -r ./out/app.zip ./app
	scp -i infra/ssh-key.pem out/app.zip ubuntu@${APP-IP}:	
	ssh -i infra/ssh-key.pem ubuntu@${APP-IP} "unzip -o app.zip && sudo pip3 install -r app/requirements.txt && sudo python3 app/app.py &"

setup-infra:
	(cd infra; terraform apply -auto-approve)

start-spark-cluster:
	ssh -i infra/ssh-key.pem ubuntu@${ETL-IP} "spark-3.0.1-bin-hadoop3.2/sbin/start-master.sh && spark-3.0.1-bin-hadoop3.2/sbin/start-slave.sh spark://${ETL-IP}:7077 -p 7070"

spark-ml-job-submit:
	/Library/Frameworks/Python.framework/Versions/3.8/bin/spark-submit \
	--master spark://${ETL-IP}:7077 \
	--packages "org.apache.hadoop:hadoop-common:3.2.0, org.apache.hadoop:hadoop-aws:3.2.0" \
	--deploy-mode client \
	etl/ml-job.py

warehouse-init-schema:
	mysql --host=${WAREHOUSE-HOST} --port=3306 --user=admin --password=admin1234 < infra/schema.sql

spark-ml-job-run:
	spark-submit \
	 etl/ml-job.py ${WAREHOUSE-HOST}		
