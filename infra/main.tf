terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 3.16.0"
    }
  }
}

provider "aws" {
  profile = "default"
  region = "us-east-1"
}

resource "aws_instance" "app" {
  ami = "ami-0885b1f6bd170450c"
  instance_type = "t2.micro"
  key_name = aws_key_pair.generated_key.key_name
  vpc_security_group_ids = [
    aws_security_group.instance.id]

  tags = {
    Name = "app"
  }

  provisioner "remote-exec" {
    script = "app-ubuntu-init.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = file("${self.key_name}.pem")
      host = self.public_ip
    }
  }
}

resource "aws_instance" "etl" {
  ami = "ami-0885b1f6bd170450c"
  instance_type = "t2.micro"
  key_name = aws_key_pair.generated_key.key_name
  vpc_security_group_ids = [
    aws_security_group.instance.id]
  tags = {
    Name = "etl"
  }

  provisioner "remote-exec" {
    script = "etl-ubuntu-init.sh"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = file("${self.key_name}.pem")
      host = self.public_ip
    }
  }
}

resource "aws_s3_bucket" "raw_db" {
  bucket = "s3-storage-dmashchenko"
  acl = "public-read"

  tags = {
    Name = "raw-db"
  }
}

resource "aws_s3_bucket_object" "object" {
  bucket = aws_s3_bucket.raw_db.bucket
  acl = "public-read"
  key = "dataset"
  source = "./test_data.csv"
}

resource "aws_db_instance" "warehouse" {
  allocated_storage = 20
  storage_type = "gp2"
  engine = "mysql"
  engine_version = "5.7"
  instance_class = "db.t2.micro"
  name = "warehouse"
  username = "admin"
  password = "admin1234"
  publicly_accessible = true
  vpc_security_group_ids = [aws_security_group.instance.id]
  skip_final_snapshot = true
}
resource "aws_security_group" "instance" {
  name = "ec2-instance"
  ingress {
    from_port = 22
    protocol = "tcp"
    to_port = 22
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  #etl-spark-master
  ingress {
    from_port = 7077
    protocol = "tcp"
    to_port = 7077
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  ingress {
    from_port = 8080
    protocol = "tcp"
    to_port = 8080
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  #spark-worker
  ingress {
    from_port = 8081
    protocol = "tcp"
    to_port = 8081
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  ingress {
    from_port = 7070
    protocol = "tcp"
    to_port = 7070
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  # Allow inbound HTTP requests
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  # Allow inbound MySql requests
  ingress {
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  # Allow all outbound requests
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }
}

resource "tls_private_key" "key_gen" {
  algorithm = "RSA"
}

resource "aws_key_pair" "generated_key" {
  key_name = "ssh-key"
  public_key = tls_private_key.key_gen.public_key_openssh
}

resource "local_file" "private_key" {
  content = tls_private_key.key_gen.private_key_pem
  filename = "ssh-key.pem"
  file_permission = "600"
}

output instance_dns_names {
  value = aws_instance.app.public_dns
}

output app_ip {
  value = aws_instance.app.public_ip
}

output etl_ip {
  value = aws_instance.etl.public_ip
}

output s3_arn {
  value = aws_s3_bucket.raw_db.arn
}

output instance_ids {
  value = aws_instance.app.id
}

output warehouse_host {
  value = aws_db_instance.warehouse.address
}
