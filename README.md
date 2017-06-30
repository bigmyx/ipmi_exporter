Prometheus IPMI Exporter
===


Requirements
---

1. Python (tested with 2.7)
2. Python [prometheus_client](https://github.com/prometheus/client_python) module
3. Docker engine (optional)


Run using Docker
---

Build the Docker image
```
$ docker build -t <hub_user>/ipmi_exporter:v1 .
```
Run the container
```
docker run \
   -p8000:8000 -d -ti \
   -e "TARGET_IPS=192.168.0.1,192.168.0.2" \
   <hub_user>/ipmi_exporter:v1
```
Verify
```
docker logs -f <CT_ID>
```
Access http://localhost:8000/metrics

You should get something like this:

```
# HELP request_processing_seconds Time spent processing request
# TYPE request_processing_seconds summary 
request_processing_seconds_count 1.0 
request_processing_seconds_sum
1.0013580322265625e-05
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge 
process_virtual_memory_bytes 171442176.0
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge 
process_resident_memory_bytes 15982592.0
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge 
process_start_time_seconds 1498853325.07
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter 
process_cpu_seconds_total 0.2
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 7.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1048576.0
# HELP ipmi_fan_speed Fan speed
# TYPE ipmi_fan_speed gauge 
ipmi_fan_speed{ip="192.168.0.1"} 6900.0 
ipmi_fan_speed{ip="192.168.0.2"} 6900.0
# HELP ipmi_cpu_temp CPU temp
# TYPE ipmi_cpu_temp gauge 
ipmi_cpu_temp{ip="192.168.0.1"} 36.0 
ipmi_cpu_temp{ip="192.168.0.2"} 36.0
# HELP ipmi_system_temp System temp
# TYPE ipmi_system_temp gauge 
ipmi_system_temp{ip="192.168.0.1"} 25.0 
ipmi_system_temp{ip="192.168.0.2"} 25.0
```

As a command
---

```
export TARGET_IPS=192.168.0.1,192.168.0.2
python ipmi_exporter.py
```

