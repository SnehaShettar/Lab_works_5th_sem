"""
Workload generator for the Library Management microservices (Checkpoint 4 + 5).

For each workload level (1, 2, 4, 8, 16 concurrent users) it:
  * sends requests to the end-to-end endpoint for DURATION seconds
  * records average / p95 response time, throughput, successful and failed requests
  * samples `docker stats` for all three containers (CPU % and memory)
Then it writes results.csv, results.md (observation table) and 4 graphs.

Run (with the containers already up):
    pip install httpx matplotlib
    python load_test.py
"""
import asyncio
import csv
import statistics
import subprocess
import threading
import time

import httpx

URL = "http://localhost:8003/loans/check/1/1"   # Client -> Loan -> Book + Member
LEVELS = [("W1", 1), ("W2", 2), ("W3", 4), ("W4", 8), ("W5", 16)]
DURATION = 20                                    # seconds per workload level
CONTAINERS = ["loan_service", "book_service", "member_service"]


# ---------------- docker stats sampling (runs in a background thread) ----------------
def to_mib(text):
    text = text.strip()
    units = {"KiB": 1 / 1024, "MiB": 1, "GiB": 1024, "kB": 1 / 1024, "MB": 1, "GB": 1024, "B": 1 / (1024 * 1024)}
    for unit in sorted(units, key=len, reverse=True):
        if text.endswith(unit):
            return float(text[: -len(unit)]) * units[unit]
    return float(text)


def sample_docker_stats(stop_event, samples):
    while not stop_event.is_set():
        try:
            out = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "{{.Name}};{{.CPUPerc}};{{.MemUsage}}"]
                + CONTAINERS,
                capture_output=True, text=True, timeout=15,
            ).stdout
        except Exception as error:
            print("  docker stats failed:", error)
            return
        for line in out.strip().splitlines():
            name, cpu, mem = line.split(";")
            samples.setdefault(name, {"cpu": [], "mem": []})
            samples[name]["cpu"].append(float(cpu.strip().rstrip("%")))
            samples[name]["mem"].append(to_mib(mem.split("/")[0]))


# ---------------- load generation ----------------
async def worker(client, end_time, latencies, counters):
    while time.perf_counter() < end_time:
        start = time.perf_counter()
        try:
            response = await client.get(URL)
            ok = response.status_code == 200
        except httpx.HTTPError:
            ok = False
        latencies.append((time.perf_counter() - start) * 1000)
        counters["ok" if ok else "failed"] += 1


async def run_level(concurrency):
    latencies, counters = [], {"ok": 0, "failed": 0}
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    async with httpx.AsyncClient(timeout=10, limits=limits) as client:
        await client.get(URL)  # warm-up request
        start = time.perf_counter()
        end_time = start + DURATION
        await asyncio.gather(*[worker(client, end_time, latencies, counters) for _ in range(concurrency)])
        elapsed = time.perf_counter() - start
    latencies.sort()
    return {
        "requests": counters["ok"] + counters["failed"],
        "successful": counters["ok"],
        "failed": counters["failed"],
        "avg_ms": statistics.mean(latencies),
        "p95_ms": latencies[int(len(latencies) * 0.95) - 1],
        "throughput": (counters["ok"] + counters["failed"]) / elapsed,
    }


def main():
    rows = []
    for label, concurrency in LEVELS:
        print(f"{label}: {concurrency} concurrent user(s) for {DURATION}s ...")
        samples, stop = {}, threading.Event()
        sampler = threading.Thread(target=sample_docker_stats, args=(stop, samples), daemon=True)
        sampler.start()
        result = asyncio.run(run_level(concurrency))
        stop.set()
        sampler.join()

        row = {"workload": label, "concurrency": concurrency, **result}
        for name in CONTAINERS:
            stats = samples.get(name, {"cpu": [0], "mem": [0]})
            row[f"{name}_cpu"] = statistics.mean(stats["cpu"] or [0])
            row[f"{name}_mem"] = statistics.mean(stats["mem"] or [0])
        rows.append(row)
        print(f"   avg {row['avg_ms']:.1f} ms | {row['throughput']:.1f} req/s | failed {row['failed']} | "
              + " | ".join(f"{n} CPU {row[n + '_cpu']:.1f}% MEM {row[n + '_mem']:.1f}MiB" for n in CONTAINERS))
        time.sleep(3)  # let containers settle between levels

    # ---------- results.csv ----------
    with open("results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow({k: round(v, 2) if isinstance(v, float) else v for k, v in row.items()})

    # ---------- results.md (observation table) ----------
    with open("results.md", "w") as f:
        f.write("| Workload | Concurrency | Requests | Avg Response (ms) | P95 (ms) | Throughput (req/s) | Failed "
                "| CPU % (loan / book / member) | Memory MiB (loan / book / member) |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            cpu = " / ".join(f"{r[n + '_cpu']:.1f}" for n in CONTAINERS)
            mem = " / ".join(f"{r[n + '_mem']:.1f}" for n in CONTAINERS)
            f.write(f"| {r['workload']} | {r['concurrency']} | {r['requests']} | {r['avg_ms']:.1f} | "
                    f"{r['p95_ms']:.1f} | {r['throughput']:.1f} | {r['failed']} | {cpu} | {mem} |\n")
    print("\nSaved results.csv and results.md")

    # ---------- graphs ----------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping graphs (pip install matplotlib)")
        return

    x = [r["concurrency"] for r in rows]

    def save(filename, title, ylabel, series):
        plt.figure(figsize=(7, 4.5))
        for name, values in series.items():
            plt.plot(x, values, marker="o", label=name)
        plt.xscale("log", base=2)
        plt.xticks(x, [str(v) for v in x])
        plt.title(title)
        plt.xlabel("Concurrent requests")
        plt.ylabel(ylabel)
        plt.grid(alpha=0.3)
        if len(series) > 1:
            plt.legend()
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print("Saved", filename)

    save("graph_response_time.png", "Concurrent Requests vs Average Response Time", "Response time (ms)",
         {"Average": [r["avg_ms"] for r in rows], "P95": [r["p95_ms"] for r in rows]})
    save("graph_throughput.png", "Concurrent Requests vs Throughput", "Requests per second",
         {"Throughput": [r["throughput"] for r in rows]})
    save("graph_cpu.png", "Concurrent Requests vs CPU Utilization", "CPU %",
         {n: [r[n + "_cpu"] for r in rows] for n in CONTAINERS})
    save("graph_memory.png", "Concurrent Requests vs Memory Utilization", "Memory (MiB)",
         {n: [r[n + "_mem"] for r in rows] for n in CONTAINERS})


if __name__ == "__main__":
    main()
