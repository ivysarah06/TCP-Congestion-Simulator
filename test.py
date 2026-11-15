from simulator import run_simulation
from metrics import calculate_all_metrics

results = run_simulation(50)

metrics = calculate_all_metrics(results)

print("\nPERFORMANCE METRICS")

for name, value in metrics.items():
    print(f"{name}: {value:.4f}")

print("\nRTT ANALYSIS")

print("Total RTT samples:", len(results["rtt_samples"]))

retransmitted_packets = {
    event["packet"]
    for event in results["packet_events"]
    if event["event"] == "retransmitted"
}

print("Unique retransmitted packets:", len(retransmitted_packets))
print("Average RTT (ms):", metrics["average_rtt_ms"])