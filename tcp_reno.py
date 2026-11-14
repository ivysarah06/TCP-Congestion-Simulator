import pandas as pd

def on_ack(tcp):
    if tcp["state"] == "Fast Recovery":
        # Exit Fast Recovery
        tcp["cwnd"] = tcp["ssthresh"]
        tcp["state"] = "Congestion Avoidance"

    elif tcp["state"] == "Slow Start":
        tcp["cwnd"] += 1

        if tcp["cwnd"] >= tcp["ssthresh"]:
            tcp["cwnd"] = tcp["ssthresh"]
            tcp["state"] = "Congestion Avoidance"

    elif tcp["state"] == "Congestion Avoidance":
        tcp["cwnd"] += 1 / tcp["cwnd"]

def on_duplicate_ack(tcp, ack_num):
    tcp["dup_ack_count"] += 1
    if tcp["dup_ack_count"] == 3:
        flight_size = tcp["flight_size"]
        tcp["ssthresh"] = max(flight_size / 2, 2)
        tcp["cwnd"] = tcp["ssthresh"] + 3
        tcp["state"] = "Fast Recovery"
        tcp["retransmit"] = True
    elif tcp["dup_ack_count"] > 3:
        if tcp["state"] == "Fast Recovery":
            tcp["cwnd"] += 1

def on_timeout(tcp, flight_size):
    tcp["ssthresh"] = max(flight_size / 2, 2)
    tcp["cwnd"] = 1.0
    tcp["state"] = "Slow Start"
    tcp["dup_ack_count"] = 0
    tcp["retransmit"] = True

# Main simulation
def simulate_tcp_reno(
    initial_cwnd=1,
    ssthresh=16,
    loss_round=10,
    loss_type="Triple Duplicate ACK",
    total_rounds=20
):

    results = []

    tcp = {
        "cwnd": float(initial_cwnd),
        "ssthresh": float(ssthresh),
        "state": "Slow Start",
        "dup_ack_count": 0,
        "last_ack": None,
        "retransmit": False,
        "flight_size": 0
    }

    for round_num in range(1, total_rounds + 1):
        event = "Normal Transmission"
        if round_num == loss_round:
            if loss_type == "Triple Duplicate ACK":
                event = "Triple Duplicate ACK"
                for _ in range(3):
                    on_duplicate_ack(tcp, 5)
            elif loss_type == "Timeout":
                event = "Retransmission Timeout"
                on_timeout(tcp)

        elif tcp["state"] == "Fast Recovery":
            tcp["cwnd"] = tcp["ssthresh"]
            tcp["state"] = "Congestion Avoidance"
            tcp["dup_ack_count"] = 0
            tcp["retransmit"] = False
            event = "Recovery Complete"

        else:
            if tcp["state"] == "Slow Start":
                event = "Slow Start"
                acknowledgements = max(1, int(tcp["cwnd"]))
            else:
                event = "Congestion Avoidance"
                acknowledgements = max(1, int(tcp["cwnd"]))
            for _ in range(acknowledgements):
                on_ack(tcp)

        results.append({
            "Round": round_num,
            "cwnd": round(tcp["cwnd"], 2),
            "ssthresh": round(tcp["ssthresh"], 2),
            "State": tcp["state"],
            "Event": event
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = simulate_tcp_reno()
    print(df)