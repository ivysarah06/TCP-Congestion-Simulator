from simulator import run_simulation
from metrics import calculate_all_metrics
from collections import Counter

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


router_counts = Counter(
    event["router"]
    for event in results["packet_events"]
    if event["event"] == "forwarded"
)

print("\nPACKETS FORWARDED BY EACH ROUTER:")

for router in ["R1", "R2", "R3", "R4", "R5"]:
    print(f"{router}: {router_counts[router]}")

print("\nPACKET DROPS BY ROUTER:")

drop_counts = Counter(
    event["router"]
    for event in results["packet_events"]
    if event["event"] == "dropped"
)

for router in ["R1", "R2", "R3", "R4", "R5"]:
    print(f"{router}: {drop_counts[router]}")