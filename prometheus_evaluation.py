from prometheus_api_client import PrometheusConnect,  MetricSnapshotDataFrame, MetricRangeDataFrame
from datetime import datetime, timedelta
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

prom = PrometheusConnect(url ="https://193.196.36.163/prometheus", disable_ssl=True)

def getMetrics(start_time, end_time, step):
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
            disk_write[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])/1000000
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

    a = np.asarray([list(cpu_usage.values()), list(mem_usage.values()), list(network.values()), list(disk_write.values()), list(processing_time.values())])
    pd.DataFrame(a).to_csv("foo.csv")

    return cpu_usage, mem_usage, network, disk_write, processing_time

# Hyperledger 
# Start and End time should be adjusted to your current run
start_time = datetime.strptime('10 Mar 2021', '%d %b %Y')
start_times = [start_time.replace(hour=8, minute=3)]
end_times = []
for i in range(5):
    hour = start_times[i].hour 
    minute = (start_times[i].minute+3) % 60
    if minute < start_times[i].minute:
        hour = (hour + 1) % 24
    end_times.append(start_time.replace(hour=hour, minute=minute))

step = "5"

hyperledger_results = [getMetrics(start_times[i], end_times[i], step) for i in range(len(start_times))]

# Fabric Star 
start_times = [start_time.replace(hour=9, minute=46)]
end_times = []
for i in range(5):
    hour = start_times[i].hour 
    minute = (start_times[i].minute+3) % 60
    if minute < start_times[i].minute:
        hour = (hour + 1) % 24
    end_times.append(start_time.replace(hour=hour, minute=minute))

step = "5"

fabricstar_results = [getMetrics(start_times[i], end_times[i], step) for i in range(len(start_times))]

# Plot
# id: [0] cpu, [1] mem, [2] network (out), [3] disk (write)
# title of plot should be adjusted accordingly
id = 2
titles = ["CPU Usage [%]", "Memory Usage [MB]", "Network Transmission (Out) [KB/s]", "Disk Usage (Write) [MB/s]"]

# compute mean
def mean(results, id):
    mean = []
    for res in results:
        vals = list(res[id].values())
        if len(mean) == 0:
            mean = vals 
        else:
            for i in range(len(vals)):
                mean[i] += vals[i]

    return [m/len(results) for m in mean]

#compute sd
def sd(results, id, mean):
    sd = []
    for res in results:
        vals = list(res[id].values())
        if len(sd) == 0:
            sd = [(mean[i] - vals[i])**2 for i in range(len(vals))]  
        else:
            for i in range(len(vals)):
                sd[i] += (mean[i] - vals[i])**2

    return [np.sqrt(s/len(results)) for s in sd]


hyperledger_mean = mean(hyperledger_results, id)
hyperledger_sd = sd(hyperledger_results, id, hyperledger_mean)
fabricstar_mean = mean(fabricstar_results, id)
fabricstar_sd = sd(fabricstar_results, id, fabricstar_mean)

nodes = [x.split("_")[1] for x in hyperledger_results[0][id].keys()]
hyperledger_mean.append(hyperledger_mean[0])
hyperledger_sd.append(hyperledger_sd[0])
fabricstar_mean.append(fabricstar_mean[0])
fabricstar_sd.append(fabricstar_sd[0])

plt.figure(figsize=(10, 8))
plt.subplot(polar=True)
theta = np.linspace(0, 2 * np.pi, len(nodes)+1)

lines, labels = plt.thetagrids(range(0, 360, int(360/len(nodes))), (nodes))
plt.tick_params(direction='out', pad=30)

plt.plot(theta, hyperledger_mean, "D-", linewidth=3)
plt.plot(theta, fabricstar_mean, "D-", linewidth=3)


plt.legend(labels=('Hyperledger', 'Fabric*'), bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.title(titles[id], y=1.05)

plt.show()