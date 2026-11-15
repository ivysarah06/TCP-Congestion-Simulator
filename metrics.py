
def calculate_throughput(results):
    # Count unique packets successfully delivered
    delivered = len(results["received_packets"])

    total_data_bits = (
        delivered * results["packet_size"] * 8
    )

    completion_time = results["completion_time"]

    if completion_time == 0:
        return 0

    # Convert bits/second to Mbps
    throughput = (
        total_data_bits / completion_time
    ) / 1_000_000

    return throughput


def calculate_packet_loss_rate(results):
    # Identify unique packet numbers that experienced a drop
    dropped_packets = {
        event["packet"]
        for event in results["packet_events"]
        if event["event"] == "dropped"
    }

    total_packets = results["total_packets"]

    if total_packets == 0:
        return 0

    loss_rate = (
        len(dropped_packets) / total_packets
    ) * 100

    return loss_rate


def calculate_average_rtt(results):
    rtt_samples = results["rtt_samples"]

    if not rtt_samples:
        return 0

    average_rtt = sum(rtt_samples) / len(rtt_samples)

    # Convert seconds to milliseconds
    return average_rtt * 1000


def calculate_completion_time(results):
    return results["completion_time"]


def calculate_all_metrics(results):
    return {
        "throughput_mbps": calculate_throughput(results),
        "packet_loss_rate": calculate_packet_loss_rate(results),
        "average_rtt_ms": calculate_average_rtt(results),
        "completion_time": calculate_completion_time(results)
    }