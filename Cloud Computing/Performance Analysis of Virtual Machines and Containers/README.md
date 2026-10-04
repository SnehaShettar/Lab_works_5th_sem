# Performance Analysis of Virtual Machines and Containers

## 1. Objective

This experiment compares the performance of identical workloads executed in an Ubuntu virtual machine and a Docker container.

The workloads evaluate CPU, memory, disk I/O, network throughput, and a FastAPI application.

## 2. Environment

### Virtual Machine
- VMware Workstation
- Ubuntu 24.04
- 4 vCPUs
- 8 GB RAM
- 40 GB virtual disk
- NAT networking

### Container
- Docker
- Ubuntu 24.04 base image
- 4 CPU limit
- 8 GB memory limit

### Benchmark Tools
- Sysbench
- fio
- iperf3
- ApacheBench
- wrk
- Python
- Pandas
- Matplotlib

## 3. Methodology

The same benchmark workloads were executed in both environments.

### CPU
Sysbench CPU prime benchmarks were executed with multiple thread counts and repeated runs.

### Memory
Sysbench memory benchmark: 1 MiB block size, 10 GiB total transfer, 4 threads, 10 repetitions.

### Disk
fio was used for sequential read, sequential write, random read, and random write workloads.

### Network
iperf3 was used for a 30-second throughput test.

Note: the network measurement used the local VM/host networking path available in this experiment, rather than an external physical network link.

### FastAPI
The FastAPI application was benchmarked using ApacheBench and wrk.

The health endpoint was tested with 10,000 requests and concurrency of 100.

## 4. Results

| Metric | VM | Container | Difference |
|---|---:|---:|---:|
| CPU | 5287.98 events/sec | 5020.43 events/sec | -5.06% |
| Memory | 97574.36 MiB/sec | 80169.43 MiB/sec | -17.84% |
| Sequential Read | 1043 MiB/sec | 1178 MiB/sec | +12.94% |
| Sequential Write | 1159 MiB/sec | 1550 MiB/sec | +33.74% |
| Random Read | 28.9 MiB/sec | 30.2 MiB/sec | +4.50% |
| Random Write | 31.8 MiB/sec | 39.7 MiB/sec | +24.84% |
| Network | 52.8 Gbits/sec | 49.7 Gbits/sec | -5.87% |
| FastAPI Health | 1871.51 req/sec | 1628.19 req/sec | -13.00% |

## 5. Graphs

Generated graphs are stored in results/figures/.

- cpu_performance.png
- memory_performance.png
- disk_performance.png
- network_performance.png
- api_performance.png

## 6. Discussion

The measured results show different performance characteristics across workloads.

The VM performed better in CPU, memory, network throughput, and the FastAPI health benchmark under the tested configuration.

The container performed better in all four measured disk workloads.

These results are specific to the experimental configuration, host system, storage path, networking setup, Docker configuration, and benchmark conditions. They should not be interpreted as universal characteristics of VMs or containers.

## 7. Reproducibility

Raw benchmark outputs are stored under results/raw/.
Processed results are stored under results/processed/.
Graphs are stored under results/figures/.
Benchmark and application files are stored under docker/, api/, scripts/, and workloads/.

## 8. Project Structure

```text
vm-vs-container-performance/
├── api/
├── docker/
├── docs/
├── results/
│   ├── raw/
│   ├── processed/
│   └── figures/
├── scripts/
├── workloads/
├── README.md
└── .gitignore
```

## 9. Conclusion

Under the tested configuration, containers showed lower CPU, memory, network, and FastAPI performance than the VM, while showing higher measured disk throughput.

The experiment demonstrates that VM-versus-container performance depends strongly on the workload and configuration.
