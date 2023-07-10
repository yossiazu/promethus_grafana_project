# monitoring project
This project involves deploying Prometheus and Grafana in a Kubernetes cluster. Within the cluster, there are RabbitMQ and Redis services that we monitor using Prometheus and visualize using Grafana. Each service has its own dashboard with specific metrics relevant to that service. Additionally, we have configured alerts to notify us in case of slightly extreme situations.

To deploy this project automatically, you can simply run the project.sh file. This script will handle the deployment of Prometheus, Grafana, RabbitMQ, Redis, and all the necessary configurations and dependencies. Once deployed, you will have a fully functional monitoring setup with dashboards for RabbitMQ and Redis, as well as alerts set up to ensure timely notifications for critical events.

## project.sh
explain in 2 parts:
### part 1:
```
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
```
The script begins by creating an array variable called NAMESPACE_NAMES with the values "redis", "rabbitmq", and "monitoring". Then, it proceeds to iterate through each element in the NAMESPACE_NAMES array using a for loop.
During each iteration, the script checks if a namespace with the current value of NAMESPACE_NAME already exists by using the kubectl get namespace "$NAMESPACE_NAME" --output=name command. The output of this command is stored in the NAMESPACE_EXISTS variable.
If NAMESPACE_EXISTS is empty, indicating that the namespace does not exist, the script creates the namespace using kubectl create namespace "$NAMESPACE_NAME" and prints a message saying that the namespace has been created.
If NAMESPACE_EXISTS is not empty, indicating that the namespace already exists, the script prints a message saying that the namespace already exists.

### part2:
```
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
```
The given set of commands sets up monitoring with Prometheus, deploys Redis and RabbitMQ using Helm, and applies configuration updates. Here's a 
summary of what each command does:

The first three commands add Helm repositories for Prometheus Community and Bitnami and update the local Helm chart repositories.

The next three commands install the following components using Helm charts:
Prometheus stack (prometheus-community/kube-prometheus-stack) in the monitoring namespace with the release name prometheus.
Redis (bitnami/redis) with version 17.11.6 in the redis namespace with the release name my-redis.
RabbitMQ (bitnami/rabbitmq) with version 12.0.4 in the rabbitmq namespace with the release name my-rabbitmq.

### (explanation about the values, alert and the configmap_cluster is in the readme of config directory )

The following two commands apply Kubernetes resource configurations:
Apply the configuration of the dashboards from config/configmap_cluster.yaml to create a ConfigMap in the monitoring namespace.
Apply the configuration of the alerts from config/alert.yaml to create alert rules in the monitoring namespace for Prometheus.

The last three commands perform upgrades to existing deployments using new configuration files:
Upgrade the Prometheus stack (prometheus-community/kube-prometheus-stack) in the monitoring namespace, applying the configuration from config/values_promethus.yaml.
Upgrade the Redis deployment (bitnami/redis) in the redis namespace, applying the configuration from config/values_redis.yaml.
Upgrade the RabbitMQ deployment (bitnami/rabbitmq) in the rabbitmq namespace, applying the configuration from config/values_rabbitmq.yaml.

## close.sh
```
#!/bin/bash

kubectl delete -f configmap_cluster.yaml -n monitoring
kubectl delete -f alert.yaml -n monitoring

helm uninstall prometheus prometheus-community/kube-prometheus-stack -n monitoring
helm uninstall my-redis bitnami/redis -n redis
helm uninstall my-rabbitmq bitnami/rabbitmq -n rabbitmq
```
Deletes a ConfigMap and alert rules from the "monitoring" namespace using kubectl delete.
Uninstalls the Prometheus stack, Redis, and RabbitMQ deployments from their respective namespaces using helm uninstall.
In summary, these commands remove Kubernetes resources and uninstall Helm deployments associated with monitoring, Prometheus, Redis, and RabbitMQ.

