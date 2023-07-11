#!/bin/bash

kubectl delete -f config/configmap_cluster.yaml -n monitoring
kubectl delete -f config/alert.yaml -n monitoring

helm uninstall my-grafana-loki bitnami/grafana-loki -n loki 
helm uninstall prometheus prometheus-community/kube-prometheus-stack -n monitoring
helm uninstall my-redis bitnami/redis -n redis
helm uninstall my-rabbitmq bitnami/rabbitmq -n rabbitmq
