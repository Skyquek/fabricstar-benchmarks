from prometheus_api_client import PrometheusConnect,  MetricSnapshotDataFrame, MetricRangeDataFrame
from datetime import datetime, timedelta
import re

prom = PrometheusConnect(url ="https://193.196.36.163/prometheus", disable_ssl=True)

start_time = datetime.strptime('08 Mar 2021', '%d %b %Y')
start_time = start_time.replace(hour=21, minute=21)

end_time = start_time.replace(minute=24)

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
    if row["instance"] not in ipDict and not row["container_label_com_docker_swarm_service_name"] in ["fabricstar_nodeexporter", "fabricstar_cadvisor", "fabricstar_caOrg1", "fabricstar_caOrg2"]:
        ipDict[row["instance"]] = row["container_label_com_docker_swarm_service_name"]

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
        if ipDict[row["instance"]] not in reducedMetrics:
            reducedMetrics[ipDict[row["instance"]]] = []
        
        reducedMetrics[ipDict[row["instance"]]].append(row["value"])

network = {}
for container in reducedMetrics:
    if re.match(".*orderer.*", str(container)) or re.match(".*kafka.*", str(container)) or re.match(".*peer.*", str(container)):
        network[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])/1000
        print(container, network[container])     

# Disk Write

print("\nDisk Write\n")

metric_data = prom.custom_query_range(
    "sum(rate(container_fs_writes_bytes_total{name=~\".+\"}[1m])) by (container_label_com_docker_swarm_service_name)",  # this is the metric name and label config
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

disk_write = {}
for container in reducedMetrics:
    if re.match(".*orderer.*", str(container)) or re.match(".*kafka.*", str(container)) or re.match(".*peer.*", str(container)):
        disk_write[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])/1000
        print(container, disk_write[container])    

# Ledger Block Processing Time

print("\nLedger Block Processing Time\n")

metric_data = prom.custom_query_range(
    "rate(ledger_block_processing_time_count[1m])",  # this is the metric name and label config
    start_time=start_time,
    end_time=end_time,
    step=step
)

metric_df = MetricRangeDataFrame(metric_data)

reducedMetrics = {}

for index, row in metric_df.iterrows():
    if row["instance"] not in reducedMetrics:
        reducedMetrics[row["instance"]] = []
    
    reducedMetrics[row["instance"]].append(row["value"])

processing_time = {}
for container in reducedMetrics:
    if re.match(".*orderer.*", str(container)) or re.match(".*kafka.*", str(container)) or re.match(".*peer.*", str(container)):
        processing_time[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])
        print(container, processing_time[container])              
