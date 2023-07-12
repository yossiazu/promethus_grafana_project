# tutorial
## I use three values files to upgrade the Helm releases of Prometheus, Redis, and RabbitMQ.

* ### values_promethus.yaml
```
  additionalDataSources: 
    - name: loki
      access: proxy
      editable: true
      orgId: 1
      type: loki
      url: http://my-grafana-loki-querier.monitoring:3100
      version: 1
    - name: redis
      type: redis-datasource
      access: proxy
      editable: true
      orgId: 1
      url: redis://my-redis-master.redis:6379
      jsonData:
          client: standalone
          poolSize: 5
          timeout: 10
          pingInterval: 0
          pipelineWindow: 0
      secureJsonData:
        password: 12345
      version: 1
...
ruleSelectorNilUsesHelmValues: false
...
serviceMonitorSelectorNilUsesHelmValues: false
```
The first change create a new data sourceses named "loki" and redis that Grafana can access (*for access redis grafana will need a password). The service for this data source is named "my-grafana-loki-querier" residing within the "monitoring" namespace, and it operates on port 3100.
The next two changes enable Prometheus to access rules and ServiceMonitors beyond the default Helm values. By setting 'ruleSelectorNilUsesHelmValues' and 'serviceMonitorSelectorNilUsesHelmValues' to false, Prometheus is configured to use the actual cluster resources for rules and ServiceMonitors rather than relying only on the Helm values. This modification provides flexibility in selecting and monitoring resources within the cluster.

* ### values_rabbitmq.yaml
```
metrics:
  enabled: true
  podAnnotations:
    prometheus.io/path: /metrics
    prometheus.io/scrape: "true"
    prometheus.io/port: "9419"
  serviceMonitor:
    enabled: true
    selector:
      app.kubernetes.io/instance: my-rabbitmq
    namespace: rabbitmq
    path: /metrics
    interval: 30s
    scrapeTimeout: 15s
  prometheusRule:
    enabled: true
    namespace: rabbitmq
```
These changes enable the scraping of RabbitMQ pod metrics with Prometheus. It establishes pod annotations, creates a ServiceMonitor with specific configurations, and activates Prometheus rules in the designated namespace. These changes support the collection and monitoring of RabbitMQ metrics, enabling better visibility and control over RabbitMQ performance.

* ### values_redis.yaml
```
auth:
  password: "12345"
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    additionalLabels:
      app.kubernetes.io/component: metrics
  prometheusRule:
    enabled: true
    namespace: "redis"
```
The first two lines define a password to redis for grafana to be able to connect direct to redis as data-source, the next changes enable the scraping of metrics from a Redis service and create a ServiceMonitor specifically for the Redis metrics-gathering service identified by the label app.kubernetes.io/component: metrics. Additionally, it enables the Prometheus rules in the redis namespace.

* ### values_loki.yaml
```
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: loki
```
The changes enable the scraping of metrics from the loki service and create a ServiceMonitor specifically for the loki metrics-gathering service.

## configmap_cluster.yaml, the dashboards.
The labeled JSON file in the config map is set as the initial dashboard for Grafana with the 'grafana_dashboard: "1"' label. Upon initialization, Grafana automatically loads and displays this predefined dashboard configuration.
i will explain every dashboard separately:

* ### CLUSTER_ANALYSIS
varibales: 'datasource: Prometheus', 'namespace: depends', 'node: depends', 'pod: depends', 'resolution: 30s, 5m , 1h', 'interval: 4h'.

1. runnig pods on the node
```
count(kube_pod_info{node="$node"})
```
Used to count the number of pods running on a specific node in a Kubernetes cluster.

2. CPU usage
```
100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
Used to calculate the CPU utilization percentage across all instances in a given time.

3. memory usage
```
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```
Used to calculate the memory utilization percentage on a node.

4. current rate of bytes received
```
sum(irate(container_network_receive_bytes_total{cluster="$cluster",namespace=~"$namespace"}[$interval:$resolution]))
```
Used to calculate the rate of network bytes received by containers within a specified cluster and namespace over a given time.

5. current rate of bytes transmitted
```
sum(irate(container_network_transmit_bytes_total{cluster="$cluster",namespace=~"$namespace"}[$interval:$resolution]))
```
Used to calculate the rate of network bytes transmitted by containers within a specified cluster and namespace over a given time.

6. container CPU usage per pod
```
sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{cluster="$cluster", node=~"$node"}) by (pod) 
```
Used to calculate the total CPU usage in seconds by containers within a specified cluster and node, grouped by the pod.

7. pod info (table)
```
sum(kube_pod_container_status_restarts_total) by(pod)
kube_pod_created{node="$node"}
```
The first column represents the sum of container restarts per pod.
The second column represents the creation time of pods on the specified node.

8. memory usage of pods (table)
```
sum(container_memory_usage_bytes{node="$node"}) by (pod) > 0
sum(rate(container_cpu_usage_seconds_total{node="$node"}[5m])) by (pod)
```
The first column calculates the sum of memory usage in bytes for containers on the specified node and grouped by pods. (The condition > 0 ensures that only pods with non-zero memory usage will be included in the result)
The second column calculates the per-second rate of change in CPU usage for containers on the specified node, averaged and grouped by pods.

* ### rabbitmq
It is important to note that this dashboard was created using the 'RabbitMQ-Overview' dashboard available in the Grafana store. The dashboard can be found at the following link: https://grafana.com/grafana/dashboards/10991-rabbitmq-overview/. The entire content and design of the dashboard are based on the pre-existing 'RabbitMQ-Overview' dashboard available in the Grafana store.

variables: 'data_sorce: Prometheus', 'namespace: rabbitmq', 'rabbitmq_cluster: rabbit@my-rabbitmq-0.my-rabbitmq-headless.rabbitmq.svc.cluster.local'.

1. Incoming messages / s
```
sum(rate(rabbitmq_global_messages_received_total[60s]) * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the rate of messages received by RabbitMQ globally, filtered by the specified RabbitMQ cluster and namespace.

2. Outgoing messages / s
```
sum(rate(rabbitmq_global_messages_redelivered_total[60s]) * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) +
sum(rate(rabbitmq_global_messages_delivered_consume_auto_ack_total[60s]) * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) +
sum(rate(rabbitmq_global_messages_delivered_consume_manual_ack_total[60s]) * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) +
sum(rate(rabbitmq_global_messages_delivered_get_auto_ack_total[60s]) * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) +
sum(rate(rabbitmq_global_messages_delivered_get_manual_ack_total[60s]) * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
By summing the results of these queries together, you will obtain the combined rate of message redelivery and delivery events in RabbitMQ, filtered by the specified RabbitMQ cluster and namespace.

3. Publishers
```
sum(rabbitmq_channels * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) - sum(rabbitmq_channel_consumers * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the difference between the total number of RabbitMQ channels and the total number of RabbitMQ channel consumers within a specified RabbitMQ cluster and namespace.. 

4. Consumers
```
sum(rabbitmq_consumers * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the total number of RabbitMQ consumers within a specified RabbitMQ cluster and namespace.

5. Connections
```
sum(rabbitmq_connections * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the total number of RabbitMQ connections within a specified RabbitMQ cluster and namespace.

6. Channels
```
sum(rabbitmq_channels * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the total number of RabbitMQ channels within a specified RabbitMQ cluster and namespace.

7. Queues
```
sum(rabbitmq_queues * on(instance) group_left(rabbitmq_cluster) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the total number of RabbitMQ queues within a specified RabbitMQ cluster and namespace.

8. Nodes
```
rabbitmq_build_info * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}
```
Used to retrieve the build information for RabbitMQ instances within a specified RabbitMQ cluster and namespace, while grouping the results by both rabbitmq_cluster and rabbitmq_node labels and create a table with all the information. 

9. Memory available before publishers blocked
```
(rabbitmq_resident_memory_limit_bytes * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) -
(rabbitmq_process_resident_memory_bytes * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the difference between the RabbitMQ resident memory limit and the RabbitMQ process resident memory for each RabbitMQ instance within a specified RabbitMQ cluster and namespace.

10. Disk space available before publishers blocked
```
rabbitmq_disk_space_available_bytes * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}
```
Used to retrieve the available disk space in bytes for each RabbitMQ instance within a specified RabbitMQ cluster and namespace. 

11. File descriptors available
```
(rabbitmq_process_max_fds * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) -
(rabbitmq_process_open_fds * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the difference between the maximum file descriptors (max_fds) and the currently open file descriptors (open_fds) for each RabbitMQ instance within a specified RabbitMQ cluster and namespace.

12. TCP sockets available
```
(rabbitmq_process_max_tcp_sockets * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) -
(rabbitmq_process_open_tcp_sockets * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"})
```
Used to calculate the difference between the maximum number of TCP sockets (max_tcp_sockets) and the currently open TCP sockets (open_tcp_sockets) for each RabbitMQ instance within a specified RabbitMQ cluster and namespace.

13. Total connections
```
rabbitmq_connections * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}
```
Used to retrieve the total number of RabbitMQ connections for each RabbitMQ instance within a specified RabbitMQ cluster and namespace.

14. Connections opened / s
```
sum(rate(rabbitmq_connections_opened_total[60s]) * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) by(rabbitmq_node)
```
Used to calculate the rate of opened RabbitMQ connections over a 60s window for each RabbitMQ node within a specified RabbitMQ cluster and namespace.

15. Connections closed / s
```
sum(rate(rabbitmq_connections_closed_total[60s]) * on(instance) group_left(rabbitmq_cluster, rabbitmq_node) rabbitmq_identity_info{rabbitmq_cluster="$rabbitmq_cluster", namespace="$namespace"}) by(rabbitmq_node)
```
Used to calculate the rate of closed RabbitMQ connections over a 60s window for each RabbitMQ node within a specified RabbitMQ cluster and namespace.

* ### redis
It is important to note that this dashboard was created using the 'Redis Dashboard for Prometheus Redis Exporter (helm stable/redis-ha)' available in the Grafana store. The dashboard can be found at the following link: https://grafana.com/grafana/dashboards/11835-redis-dashboard-for-prometheus-redis-exporter-helm-stable-redis-ha/. The entire content and design of the dashboard are based on the pre-existing 'Redis Dashboard for Prometheus Redis Exporter (helm stable/redis-ha)' dashboard available in the Grafana store.

variables: 'prometheus: Prometheus', 'namespace: redis', 'pod_name: rmy-redis-master-0, my-redis-replicas-2, my-redis-replicas-1, my-redis-replicas-0', 'instance: $metrics: redis_up{namespace="$namespace", pod="$pod_name"}'

1. uptime
```
max(max_over_time(redis_uptime_in_seconds{instance=~"$instance"}[$__interval]))
```
Used to calculate the maximum value of the maximum uptime in seconds for Redis instances over a given time interval.

2. Clients
```
redis_connected_clients{instance=~"$instance"}
```
Used to retrieve the number of connected clients for Redis instances that match the instance variable.

3. Memory Usage
```
100 * (redis_memory_used_bytes{instance=~"$instance"}  / redis_memory_max_bytes{instance=~"$instance"} )
```
Used to calculate the memory utilization percentage for Redis instances that match the instance variable.

4. Commands Executed / sec
```
rate(redis_commands_processed_total{instance=~"$instance"}[1m])
```
Used to calculate the per-second rate of Redis commands processed for Redis instances that match the instance variable. The rate is calculated over a 1m time window.

5. Hits / Misses per Sec
```
irate(redis_keyspace_hits_total{instance=~"$instance"}[5m])
```
Used to calculate the per-second rate of Redis keyspace hits for Redis instances that match the instance variable. The rate is calculated over a 5m time window.

6. Total Memory Usage
```
redis_memory_used_bytes{instance=~"$instance"} 
```
Used to retrieve the current memory usage in bytes for Redis instances that match the instance variable.

7. Network I/O
```
rate(redis_net_input_bytes_total{instance=~"$instance"}[5m])
```
Used to calculate the per-second rate of Redis network input bytes for Redis instances that match the instance variable. The rate is calculated over a 5m time window.

8. Redis connected clients
```
redis_connected_clients{instance="$instance"}
```
Used to retrieve the current number of connected clients for a specific Redis instance identified by the instance variable.

9. Total Items per DB
```
sum (redis_db_keys{instance=~"$instance"}) by (db)
```
Used to calculate the sum of Redis keys grouped by the database (db) for Redis instances that match the instance variable.

* ### Loki Dashboard quick search
It is worth mentioning that I discovered this dashboard in the Grafana store. You can access the dashboard by following this link: https://grafana.com/grafana/dashboards/12019-loki-dashboard-quick-search/. The entire dashboard was obtained from that source.

variables: 'namespace: (metric: kube_pod_info)', 'pod: (metric: container_network_receive_bytes_total{namespace=~"$namespace"})', 'search: level=warn'.

1.
```
sum(count_over_time({namespace="$namespace", instance=~"$pod"} |~ "$search"[$__interval]))
```
 This Loki query counts the number of log entries over time, filtered by namespace, pod, and a specific search pattern.

2.
```
{namespace="$namespace", instance=~"$pod"} |~ "$search"
```
The query retrieves log entries that belong to the specified namespace, match the instance or pod name pattern, and contain the specified search pattern.

## alerts.yaml
This file configure the following alert rules under the group "myalerts":

alert1: This alert calculates the percentage of CPU used by the node. It triggers a warning (severity: warning) when the CPU usage is very high (more than 70%) for at least 2 minutes.
```
    - alert: alert1
      annotations:
        description: calculates the percentage of CPU used by the node.
        summary: CPU usage is very high.
      expr: |
        100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 70
      for: 2m
      labels:
        severity: warning
```
alert2: This alert calculates the percentage of memory used by the node. It triggers a warning when the memory usage is very high (more than 70% in use) for at least 2 minutes.
```
    - alert: alert2
      annotations:
        description: calculates the percentage of memory used by the node.
        summary: memory usage is very high.
      expr: |
        ((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100) > 70
      for: 2m
      labels:
        severity: warning
```
alert3: This alert calculates the number of restarts for each pod. It triggers a warning when a pod has made more than 15 restarts within a 2m window.
```
    - alert: alert3
      annotations:
        description: calculates the number of restarts evrey pod have.
        summary: this pod made more then 15 restarts.
      expr: |
        sum(kube_pod_container_status_restarts_total) by(pod) > 15
      for: 2m
      labels:
        severity: warning
```


