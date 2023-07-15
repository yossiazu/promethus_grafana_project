import subprocess

def create_namespace(namespaces):
    for namespace in namespaces:
        try:
            subprocess.run(['kubectl', 'create', 'namespace', namespace], check=False)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1 and "AlreadyExists" in e.stderr.decode():
                print(f"Namespace '{namespace}' already exists. Skipping creation.")
            else:
                raise
            
def add_repo_prometheus_community():
    subprocess.run(['helm', 'repo', 'add', 'prometheus-community', 'https://prometheus-community.github.io/helm-charts'])
    subprocess.run(['helm', 'repo', 'update'])
    
def add_repo_prometheus_community_and_bitnami():
    subprocess.run(['helm', 'repo', 'add', 'prometheus-community', 'https://prometheus-community.github.io/helm-charts'])
    subprocess.run(['helm', 'repo', 'add', 'bitnami', 'https://charts.bitnami.com/bitnami'])
    subprocess.run(['helm', 'repo', 'update'])

def deploy_prometheus():
    subprocess.run(['helm', 'install', 'prometheus', 'prometheus/kube-prometheus-stack', '-n', 'monitoring', '--values', 'config/values_promethus.yaml'])

def deploy_loki():
    subprocess.run(['helm', 'install', 'my-grafana-loki', 'bitnami/grafana-loki', '--version', '2.10.0', '-n', 'monitoring', '--values', 'config/values_loki.yaml'])

def deploy_redis():
    subprocess.run(['helm', 'install', 'my-redis', 'bitnami/redis', '--version', '17.11.6', '-n', 'redis', '--values', 'config/values_redis.yaml']) 

def deploy_rabbitmq():
    subprocess.run(['helm', 'install', 'my-rabbitmq', 'bitnami/rabbitmq', '--version', '12.0.4', '-n', 'rabbitmq', '--values', 'config/values_rabbitmq.yaml'])
    
def alert_and_dashboards():
    subprocess.run(['kubectl', 'apply', '-f', "config/alert.yaml"])
    subprocess.run(['kubectl', 'apply', '-f', "config/configmap_cluster.yaml"])   

def delete_namespace():
    namespaces = ["monitoring", "redis", "rabbitmq"]
    for namespace in namespaces:
        subprocess.run(['kubectl', 'delete', 'namespace', namespace, '--ignore-not-found'])

def delete_components():
    components = {
    "monitoring": ["prometheus", "my-grafana-loki"],
    "redis": ["my-redis"],
    "rabbitmq": ["my-rabbitmq"]
    }
    for namespace, component_list in components.items():
        for component in component_list:
            subprocess.run(['helm', 'uninstall', component, '-n', namespace])

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

if __name__ == "__main__":
    main()
