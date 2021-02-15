PYTHON = python3

$(eval APP-IP :=  $(shell cd infra; terraform output instance_ips))

app-package:
	mkdir -p out
	zip -r ./out/app.zip ./app

app-deploy:
	scp -i infra/ssh-key.pem out/app.zip ubuntu@${APP-IP}:	
	ssh -i infra/ssh-key.pem ubuntu@${APP-IP} "unzip app.zip && sudo pip3 install -r app/requirements.txt && sudo python3 app/app.py &"
setup-infra:
	(cd infra; terraform apply -auto-approve)

login:
	
