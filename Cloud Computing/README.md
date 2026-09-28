# Cloud Computing

This directory contains the laboratory experiments and practical work
completed for the Cloud Computing course.

## Experiments

### 01. Hypervisors

This experiment covers the performance analysis and practical study of
Type-1 and Type-2 hypervisors.

#### Type-1 Hypervisor
- Hypervisor: Proxmox VE
- Contains VM configuration, VM execution, and system configuration evidence.
- Refer to the `Hypervisor/TYPE-1/` directory for screenshots and results.

#### Type-2 Hypervisor
- Hypervisor: Oracle VirtualBox
- Guest OS: Ubuntu 24.04
- Contains VM configuration, CPU, memory, storage, resource monitoring,
  Sysbench, and benchmark evidence.
- Refer to the `Hypervisor/TYPE-2/` directory for screenshots and results.

### 02. Performance Analysis of Virtual Machines and Containers

This experiment compares virtual machines and Docker containers using
CPU, memory, disk, network, and application workloads.

The FastAPI workload is included as part of the application performance
analysis.

## Directory Structure

```text
Cloud Computing/
├── README.md
├── Hypervisor/
│   ├── TYPE-1/
│   └── TYPE-2/
└── Performance Analysis of Virtual Machines and Containers/
    └── FastAPI/

## Tools Used

- Proxmox VE
- Oracle VirtualBox
- Ubuntu 24.04
- Docker
- Sysbench
- FIO
- iperf3
- FastAPI
- Python

