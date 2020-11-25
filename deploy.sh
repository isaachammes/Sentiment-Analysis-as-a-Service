#!/bin/sh
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml
kubectl apply -f worker/worker-deployment.yaml
kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f database/mysql-deployment.yaml
kubectl apply -f database/mysql-service.yaml
