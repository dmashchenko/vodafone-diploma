PYTHON = python3

$(eval APP-IP :=  $(shell cd infra; terraform output app_ip))
$(eval ETL-IP :=  $(shell cd infra; terraform output etl_ip))

app-package:
	mkdir -p out
	zip -r ./out/app.zip ./app

app-deploy:
	scp -i infra/ssh-key.pem out/app.zip ubuntu@${APP-IP}:	
	ssh -i infra/ssh-key.pem ubuntu@${APP-IP} "unzip app.zip && sudo pip3 install -r app/requirements.txt && sudo python3 app/app.py &"

setup-infra:
	(cd infra; terraform apply -auto-approve)

start-spark-cluster:
	ssh -i infra/ssh-key.pem ubuntu@${ETL-IP} "spark-3.0.1-bin-hadoop3.2/sbin/start-master.sh && spark-3.0.1-bin-hadoop3.2/sbin/start-slave.sh spark://${ETL-IP}:7077 -p 7070"
	
