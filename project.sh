#!/bin/bash
NAMESPACE_NAMES=("redis" "rabbitmq" "monitoring")

for NAMESPACE_NAME in "${NAMESPACE_NAMES[@]}"; do
  NAMESPACE_EXISTS=$(kubectl get namespace "$NAMESPACE_NAME" --output=name 2>/dev/null)

  if [[ -z "$NAMESPACE_EXISTS" ]]; then
    kubectl create namespace "$NAMESPACE_NAME"
    echo "Namespace '$NAMESPACE_NAME' created."
  else
    echo "Namespace '$NAMESPACE_NAME' already exists."
  fi
done

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update


helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
helm install my-redis bitnami/redis --version 17.11.6 -n redis
helm install my-rabbitmq bitnami/rabbitmq --version 12.0.4 -n rabbitmq

kubectl apply -f config/configmap_cluster.yaml -n monitoring
kubectl apply -f config/alert.yaml -n monitoring 

helm upgrade prometheus prometheus-community/kube-prometheus-stack -n monitoring -f config/values_promethus.yaml
helm upgrade my-redis bitnami/redis -n redis --values config/values_redis.yaml
helm upgrade my-rabbitmq bitnami/rabbitmq -n rabbitmq --values config/values_rabbitmq.yaml

