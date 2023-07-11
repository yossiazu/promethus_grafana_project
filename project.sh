#!/bin/bash
NAMESPACE_NAMES=("redis" "rabbitmq" "monitoring" "loki")

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

helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --values config/values_promethus.yaml
helm install my-grafana-loki bitnami/grafana-loki --version 2.10.0 -n loki --values values_loki.yaml
helm install my-redis bitnami/redis --version 17.11.6 -n redis --values config/values_redis.yaml
helm install my-rabbitmq bitnami/rabbitmq --version 12.0.4 -n rabbitmq --values config/values_rabbitmq.yaml

kubectl apply -f config/configmap_cluster.yaml -n monitoring
kubectl apply -f config/alert.yaml -n monitoring 



