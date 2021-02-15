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

resource "aws_instance" "instance" {
  ami = "ami-0885b1f6bd170450c"
  instance_type = "t2.micro"
  key_name = aws_key_pair.generated_key.key_name
  vpc_security_group_ids = [
    aws_security_group.instance.id]
  //  user_data = file("app-ubuntu-init.sh")
  count = 1
  tags = {
    Name = "station-map-app-{count.index}"
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

resource "aws_security_group" "instance" {
  name = "ec2-instance"
  ingress {
    from_port = 22
    protocol = "tcp"
    to_port = 22
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
  value = aws_instance.instance[*].public_dns
}

output instance_ips {
  value = aws_instance.instance[*].public_ip
}

output instance_ids {
  value = aws_instance.instance[*].id
}
