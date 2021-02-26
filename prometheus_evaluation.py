from prometheus_api_client import PrometheusConnect,  MetricSnapshotDataFrame, MetricRangeDataFrame
from datetime import datetime, timedelta

prom = PrometheusConnect(url ="https://193.196.36.163/prometheus", disable_ssl=True)

start_time = datetime.strptime('25 Feb 2021', '%d %b %Y')
start_time = start_time.replace(hour=21, minute=5)

end_time = start_time.replace(minute=10)

print(start_time)
print(end_time)

step = "5"

# CPU Usage

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
    cpu_usage[container] = sum([float(x) for x in reducedMetrics[container]])/len(reducedMetrics[container])*100
    print(container, cpu_usage[container])

# Memory Usage

