# MONITORING PROJECT
This project involves deploying Prometheus, Grafana and loki in a Kubernetes cluster. Within the cluster, there are RabbitMQ and Redis services that we monitor using Prometheus and loki, and visualize using Grafana. Each service has its own dashboard with specific metrics relevant to that service. Additionally, we have configured alerts to notify us in case of slightly extreme situations.

To deploy this project automatically, you can simply run the project.sh file. This script will handle the deployment of Prometheus, loki, Grafana, RabbitMQ, Redis, and all the necessary configurations and dependencies. Once deployed, you will have a fully functional monitoring setup with dashboards for RabbitMQ, Redis and logs 0f the cluster using loki, as well as alerts set up to ensure timely notifications for critical events.

## start.py
The code aims to provide a menu-driven approach to deploy and remove various components and configure monitoring-related functionalities using Kubernetes and Helm.

### the functions
```
import subprocess
```
The subprocess module allows you to create new processes, connect to their input/output/error pipes, and obtain their return codes.

```
def create_namespace(namespaces):
    for namespace in namespaces:
        try:
            subprocess.run(['kubectl', 'create', 'namespace', namespace], check=False)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1 and "AlreadyExists" in e.stderr.decode():
                print(f"Namespace '{namespace}' already exists. Skipping creation.")
            else:
                raise
```
This function tries to create each namespace using kubectl, handles the specific case when the namespace already exists, and raises exceptions for any other errors encountered during the process.

```
def add_repo_prometheus_community():
    subprocess.run(['helm', 'repo', 'add', 'prometheus-community', 'https://prometheus-community.github.io/helm-charts'])
    subprocess.run(['helm', 'repo', 'update'])
```
This function ensures that the Prometheus Community Helm chart repository is added and its repository cache is updated, allowing users to easily install and manage Prometheus-related Helm charts from that repository.

```
def add_repo_prometheus_community_and_bitnami():
    subprocess.run(['helm', 'repo', 'add', 'prometheus-community', 'https://prometheus-community.github.io/helm-charts'])
    subprocess.run(['helm', 'repo', 'add', 'bitnami', 'https://charts.bitnami.com/bitnami'])
    subprocess.run(['helm', 'repo', 'update'])
```
This function adds both the Prometheus Community and Bitnami Helm chart repositories and updates the local repository cache.

```
def deploy_prometheus():
    subprocess.run(['helm', 'install', 'prometheus', 'prometheus/kube-prometheus-stack', '-n', 'monitoring', '--values', 'config/values_promethus.yaml'])
```
The 'deploy_prometheus' function deploys the Prometheus monitoring system using Helm in the monitoring namespace.

```
def deploy_loki():
    subprocess.run(['helm', 'install', 'my-grafana-loki', 'bitnami/grafana-loki', '--version', '2.10.0', '-n', 'monitoring', '--values', 'config/values_loki.yaml'])
```
The 'deploy_loki' function deploys the loki monitoring system using Helm in the monitoring namespace.

```
def deploy_redis():
    subprocess.run(['helm', 'install', 'my-redis', 'bitnami/redis', '--version', '17.11.6', '-n', 'redis', '--values', 'config/values_redis.yaml']) 
```
The 'deploy_redis' function deploys redis system using Helm in the redis namespace.

```
def deploy_rabbitmq():
    subprocess.run(['helm', 'install', 'my-rabbitmq', 'bitnami/rabbitmq', '--version', '12.0.4', '-n', 'rabbitmq', '--values', 'config/values_rabbitmq.yaml'])
```
The 'deploy_rabbitmq' function deploys rabbitmq system using Helm in the rabbitmq namespace.

```
def alert_and_dashboards():
    subprocess.run(['kubectl', 'apply', '-f', "config/alert.yaml", "-n", "monitoring"])
    subprocess.run(['kubectl', 'apply', '-f', "config/configmap_cluster.yaml", "-n", "monitoring" ])    
```
The 'alert_and_dashboards' function deploys the alert.yaml and the configmap_cluster.yaml in the monitoring namespace.

```
def delete_namespace():
    namespaces = ["monitoring", "redis", "rabbitmq"]
    for namespace in namespaces:
        subprocess.run(['kubectl', 'delete', 'namespace', namespace, '--ignore-not-found'])
```
The 'delete_namespace' function deletes Kubernetes namespaces using the kubectl command.

```
def delete_components():
    components = {
    "monitoring": ["prometheus", "my-grafana-loki"],
    "redis": ["my-redis"],
    "rabbitmq": ["my-rabbitmq"]
    }
    for namespace, component_list in components.items():
        for component in component_list:
            subprocess.run(['helm', 'uninstall', component, '-n', namespace])
```
The delete_components function uninstalls Helm chart releases for specific components within different namespaces. It uses a dictionary that maps namespaces to lists of component names. The function iterates over the dictionary, executing the helm uninstall command for each component in its associated namespace.

### main
```
def main():
    choice = input("Please choose an action:\n1. Deploy components\n2. Close all deploy components\nYour choice (1/2): ")

    if choice == "1":
        deploy_choice = input("Please choose a deployment option:\n1. Prometheus only\n2. Prometheus and Loki\n3. Prometheus, Loki, and Redis\n4. Prometheus, Loki, and RabbitMQ\n5. Prometheus, Loki, Redis, and RabbitMQ\nYour choice (1/2/3/4/5): ")
        if deploy_choice == "1":
            namespaces = ["monitoring"]
            create_namespace(namespaces)
            add_repo_prometheus_community()
            deploy_prometheus()
            alert_and_dashboards()
        
        elif deploy_choice == "2":
            namespaces = ["monitoring"]
            create_namespace(namespaces)
            add_repo_prometheus_community_and_bitnami()
            deploy_prometheus()
            deploy_loki()
            alert_and_dashboards()
        
        elif deploy_choice == "3":
            namespaces = ["monitoring", "redis"]
            create_namespace(namespaces)
            add_repo_prometheus_community_and_bitnami()
            deploy_prometheus()
            deploy_loki()
            deploy_redis()
            alert_and_dashboards()
        
        elif deploy_choice == "4":
            namespaces = ["monitoring", "rabbitmq"]
            create_namespace(namespaces)
            add_repo_prometheus_community_and_bitnami()
            deploy_prometheus()
            deploy_loki()
            deploy_rabbitmq()
            alert_and_dashboards()
        
        elif deploy_choice == "5":
            namespaces = ["monitoring", "redis", "rabbitmq"]
            create_namespace(namespaces)
            add_repo_prometheus_community_and_bitnami()
            deploy_prometheus()
            deploy_loki()
            deploy_redis()
            deploy_rabbitmq()
            alert_and_dashboards()
        
        else:
            print("Invalid choice. Please choose a valid option (1/2/3/4/5).")
            return
```
The function asks the user to choose an action by inputting a number (1 or 2). If the choice is 1, it proceeds with the deployment of components. If the choice is 2, it closes all deployed components.
If the user selects to deploy components (choice 1), the function prompts for a deployment option (1, 2, 3, 4, or 5) to specify which components to deploy.
Based on the selected deployment option, the function executes different functions and sets up namespaces, adds Helm chart repositories, deploys Prometheus, Loki, Redis, RabbitMQ, and sets up alerts and dashboards accordingly.
If the user selects an invalid option, the function prints an error message and returns.

```
    elif choice == "2":
        delete_choice = input("Please choose what to delete:\n1. all the components but leave the namespaces\n2. all the namespaces\nYour choice (1/2):")
        if delete_choice == "1":
            delete_components()
        elif delete_choice == "2":
            delete_namespace()
        else:
            print("Invalid choice. Please choose a valid option (1/2).")
    else:
        print("Invalid choice. Please choose a valid option (1/2).")
```
The function prompts the user to choose what to delete by inputting a number (1 or 2).
If the user selects option 1, it executes the 'delete_components' function. This function uninstalls the Helm chart releases for specific components within different namespaces.
If the user selects option 2, it executes the 'delete_namespace' function. This function deletes the specified Kubernetes namespaces.
If the user selects an invalid option, the function prints an error message.

## project.sh
### PART 1:
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

### PART 2:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --values config/values_promethus.yaml
helm install my-grafana-loki bitnami/grafana-loki --version 2.10.0 -n monitoring --values config/values_loki.yaml
helm install my-redis bitnami/redis --version 17.11.6 -n redis --values config/values_redis.yaml
helm install my-rabbitmq bitnami/rabbitmq --version 12.0.4 -n rabbitmq --values config/values_rabbitmq.yaml

kubectl apply -f config/configmap_cluster.yaml -n monitoring
kubectl apply -f config/alert.yaml -n monitoring 
```
The given set of commands sets up monitoring with Prometheus,loki and grafana , deploys Redis and RabbitMQ using Helm, and applies configuration updates. Here's a 
summary of what each command does:

The first four commands add Helm repositories for Prometheus Community and Bitnami and update the local Helm chart repositories.

The next three commands install the following components using Helm charts with new values:
Prometheus stack (prometheus-community/kube-prometheus-stack) in the monitoring namespace with the release name prometheus and applies the configuration values specified in the 'values_prometheus.yaml'.
loki (bitnamin/grafana-loki) with version 2.10.0 in the monitoring namespace with the release name my-grafana-loki and applies the configuration values specified in the values_loki.yaml.
Redis (bitnami/redis) with version 17.11.6 in the redis namespace with the release name my-redis and applies the configuration values specified in the values_redis.yaml.
RabbitMQ (bitnami/rabbitmq) with version 12.0.4 in the rabbitmq namespace with the release name my-rabbitmq and applies the configuration values specified in the values_rabbitmq.yaml.

### (explanation about the values, alert and the configmap_cluster is in the readme file of the config directory )

The following two commands apply Kubernetes resource configurations:
Apply the configuration of the dashboards from config/configmap_cluster.yaml to create a ConfigMap in the monitoring namespace.
Apply the configuration of the alerts from config/alert.yaml to create alert rules in the monitoring namespace for Prometheus.

## close.sh
```
#!/bin/bash

kubectl delete -f config/configmap_cluster.yaml -n monitoring
kubectl delete -f cofig/alert.yaml -n monitoring

helm uninstall prometheus prometheus-community/kube-prometheus-stack -n monitoring
helm uninstall my-grafana-loki bitnami/grafana-loki -n monitoring
helm uninstall my-redis bitnami/redis -n redis
helm uninstall my-rabbitmq bitnami/rabbitmq -n rabbitmq
```
Deletes a ConfigMap and alert rules from the "monitoring" namespace using kubectl delete.
Uninstalls the Prometheus stack, loki, Redis, and RabbitMQ deployments from their respective namespaces using helm uninstall.
In summary, these commands remove Kubernetes resources and uninstall Helm deployments associated with monitoring, Prometheus, loki, Redis, and RabbitMQ.

