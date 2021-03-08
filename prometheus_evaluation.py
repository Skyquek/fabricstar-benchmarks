from prometheus_api_client import PrometheusConnect,  MetricSnapshotDataFrame, MetricRangeDataFrame
from datetime import datetime, timedelta
import re

prom = PrometheusConnect(url ="https://193.196.36.163/prometheus", disable_ssl=True)

start_time = datetime.strptime('08 Mar 2021', '%d %b %Y')
start_time = start_time.replace(hour=20, minute=4)

end_time = start_time.replace(minute=7)

print(start_time)
print(end_time)

step = "5"

# CPU Usage

print("\nCPU Usage\n")

metric_data = prom.custom_query_range(
    "sum(rate(container_cpu_usage_seconds_total{name=~\".+\"}[30s])) by (container_label_com_docker_swarm_service_name, instance)",  # this is the metric name and label config
    start_time=start_time,
    end_time=end_time,
    step=step
)

metric_df = MetricRangeDataFrame(metric_data)

ipDict = {}
reducedMetrics = {}

for index, row in metric_df.iterrows():
    if row["container_label_com_docker_swarm_service_name"] not in ipDict:
        ipDict[row["container_label_com_docker_swarm_service_name"]] = row["instance"]

    if row["container_label_com_docker_swarm_service_name"] not in reducedMetrics:
        reducedMetrics[row["container_label_com_docker_swarm_service_name"]] = []
    
    reducedMetrics[row["container_label_com_docker_swarm_service_name"]].append(row["value"])

cpu_usage = {}
for container in reducedMetrics:
    if re.match(".*orderer.*", str(container)) or re.match(".*kafka.*", str(container)) or re.match(".*peer.*", str(container)):
        cpu_usage[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])*100
        print(container, cpu_usage[container])

# Memory Usage

print("\nMemory Usage\n")

metric_data = prom.custom_query_range(
    "sum(container_memory_rss{name=~\".+\"}) by (container_label_com_docker_swarm_service_name)",  # this is the metric name and label config
    start_time=start_time,
    end_time=end_time,
    step=step
)

metric_df = MetricRangeDataFrame(metric_data)

reducedMetrics = {}

for index, row in metric_df.iterrows():
    if row["container_label_com_docker_swarm_service_name"] not in reducedMetrics:
        reducedMetrics[row["container_label_com_docker_swarm_service_name"]] = []
    
    reducedMetrics[row["container_label_com_docker_swarm_service_name"]].append(row["value"])

mem_usage = {}
for container in reducedMetrics:
    if re.match(".*orderer.*", str(container)) or re.match(".*kafka.*", str(container)) or re.match(".*peer.*", str(container)):
        mem_usage[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])/1000000
        print(container, mem_usage[container])


# Network Transmission

print("\nNetwork Transmission\n")

metric_data = prom.custom_query_range(
    "sum(rate(container_network_transmit_bytes_total{instance=~\".+\"}[1m])) by (instance)",  # this is the metric name and label config
    start_time=start_time,
    end_time=end_time,
    step=step
)

metric_df = MetricRangeDataFrame(metric_data)

reducedMetrics = {}

for index, row in metric_df.iterrows():
    if row["instance"] in ipDict:
        if row["instance"] not in reducedMetrics:
            reducedMetrics[ipDict[row["instance"]]] = []
        
        reducedMetrics[ipDict[row["instance"]]].append(row["value"])

network = {}
for container in reducedMetrics:
    if re.match(".*orderer.*", str(container)) or re.match(".*kafka.*", str(container)) or re.match(".*peer.*", str(container)):
        network[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])/1000000
        print(container, network[container])        