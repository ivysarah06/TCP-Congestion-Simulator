
from network import Network


def run_simulation(total_packets=50):
    # Create a fresh network for each simulation
    network = Network()

    # Execute the complete simulation
    network.start_transfer(total_packets)

    # Collect the simulation results
    results = {
        "total_packets": total_packets,
        "completion_time": network.current_time,
        "delivered_packets": network.delivered_packets,
        "received_packets": sorted(network.received_packets),
        "cwnd_history": network.cwnd_history,
        "state_history": network.state_history,
        "packet_events": network.packet_events,
        "rtt_samples": network.rtt_samples,
        "packet_size": network.packet_size
    }

    return results

from simulator import run_simulation

results = run_simulation(50)

print("Completion Time:", results["completion_time"])
print("Delivered Packets:", results["delivered_packets"])
print("CWND Samples:", len(results["cwnd_history"]))
print("Packet Events:", len(results["packet_events"]))