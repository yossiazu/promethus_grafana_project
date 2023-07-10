#!/bin/bash

kubectl delete -f configmap_cluster.yaml -n monitoring
kubectl delete -f alert.yaml -n monitoring

helm uninstall prometheus prometheus-community/kube-prometheus-stack -n monitoring
helm uninstall my-redis bitnami/redis -n redis
helm uninstall my-rabbitmq bitnami/rabbitmq -n rabbitmq