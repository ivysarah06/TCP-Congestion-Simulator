import heapq
from collections import deque


class Acknowledgement:
    def __init__(self, ack_number, size=40):
        self.ack_number = ack_number
        self.size = size
        self.status = "Created"
        self.queue_entry_time = 0.0


class Packet:
    def __init__(self, sequence_number, size):
        self.sequence_number = sequence_number
        self.size = size
        self.creation_time = 0.0
        self.transmission_time = None
        self.arrival_time = None
        self.status = "Created"
        # Event scheduler
        self.event_queue = []
        self.current_time = 0.0
        self.event_counter = 0


class Link:
    def __init__(self, distance, bandwidth):
        self.distance = distance * 1000  # km to metres
        self.bandwidth = bandwidth * 1_000_000  # Mbps to bps
        self.propagation_speed = 2 * 10**8
        # Event scheduler
        self.event_queue = []
        self.current_time = 0.0
        self.event_counter = 0
    def calculate_transmission_delay(self, packet):
        packet_size_bits = packet.size * 8
        transmission_delay = packet_size_bits / self.bandwidth
        return transmission_delay
    def calculate_propagation_delay(self):
        propagation_delay = self.distance / self.propagation_speed
        return propagation_delay
    def calculate_total_delay(self, packet):
        transmission = self.calculate_transmission_delay(packet)
        propagation = self.calculate_propagation_delay()
        return transmission + propagation
    

class Router:
    def __init__(self, name, buffer_capacity, forwarding_rate, processing_delay):
        self.name = name
        self.buffer_capacity = buffer_capacity
        # Convert Mbps to bits per second
        self.forwarding_rate = forwarding_rate * 1_000_000
        # Convert milliseconds to seconds
        self.processing_delay = processing_delay / 1000
        self.queue = deque()
        # Track the packet currently being forwarded
        self.active_packet = None
        self.busy_until = 0.0
        self.dropped_packets = 0
        self.forwarded_packets = 0
        # Event scheduler
        self.event_queue = []
        self.current_time = 0.0
        self.event_counter = 0

    def receive_packet(self, packet, current_time):
        # Buffer capacity includes the active packet
        packets_in_router = len(self.queue)
        if self.active_packet is not None:
            packets_in_router += 1
        if packets_in_router >= self.buffer_capacity:
            self.dropped_packets += 1
            packet.status = "Dropped"
            return False
        packet.queue_entry_time = current_time
        packet.status = "Queued"
        self.queue.append(packet)
        return True
    
    def _start_next_packet(self, start_time):
        packet = self.queue.popleft()
        packet.queuing_delay = start_time - packet.queue_entry_time
        packet.processing_delay = self.processing_delay
        packet.transmission_delay = (packet.size * 8 / self.forwarding_rate)
        packet.forwarding_start_time = start_time
        total_service_time = (packet.processing_delay + packet.transmission_delay)
        self.active_packet = packet
        self.busy_until = start_time + total_service_time
        packet.status = "Forwarding"
    def process_queue(self, current_time):
        forwarded = []
        while True:
            # Start forwarding if the router is idle
            if self.active_packet is None:
                if not self.queue:
                    break
                self._start_next_packet(current_time)
            # The active packet has not finished forwarding yet
            if self.busy_until > current_time:
                break
            # Forwarding is complete
            packet = self.active_packet
            packet.forwarding_finish_time = self.busy_until
            packet.status = "Forwarded"
            forwarded.append(packet)
            self.forwarded_packets += 1
            # Router becomes available
            next_start_time = self.busy_until
            self.active_packet = None
            # Continue with the next queued packet, if any
            if self.queue:
                self._start_next_packet(next_start_time)
        return forwarded


class Network:

    def __init__(self):
        self.routers = [
            Router("R1", 10, 10, 1),
            Router("R2", 5, 2, 1),
            Router("R3", 10, 10, 1)
        ]
        # Create the four links
        self.links = [
            Link(10, 10),   # Sender -> R1
            Link(50, 10),   # R1 -> R2
            Link(50, 10),   # R2 -> R3
            Link(10, 10)    # R3 -> Receiver
        ]
        self.sender_link_available_time = 0.0
        # Reverse-direction output queues
        self.ack_routers = [
        Router("R3_ACK", 10, 10, 1),
        Router("R2_ACK", 5, 2, 1),
        Router("R1_ACK", 10, 10, 1)
        ]
        # Reverse link transmission availability
        self.ack_link_available_time = 0.0
        # Receiver information
        self.expected_sequence = 1
        self.received_packets = set()
        # Network statistics
        self.delivered_packets = 0
        self.generated_acks = []
        # Event scheduler
        self.event_queue = []
        self.current_time = 0.0
        self.event_counter = 0
        # TCP sender state
        self.tcp = {
            "cwnd": 1.0,
            "ssthresh": 16.0,
            "state": "Slow Start",
            "dup_ack_count": 0,
            "last_ack": 1,
            "retransmit": False
        }
        # Data collection for dashboard and analysis
        self.cwnd_history = [
            {
                "time": self.current_time,
                "cwnd": self.tcp["cwnd"],
                "ssthresh": self.tcp["ssthresh"]
            }
        ]
        self.state_history = [
            {
                "time": self.current_time,
                "state": self.tcp["state"]
            }
        ]
        self.packet_events = []
        # Sender information
        self.next_sequence = 1
        self.total_packets = 10
        self.packet_size = 1500
        # Track unacknowledged packets
        self.unacked_packets = {}
        # RTT measurements
        self.rtt_samples = []
        self.rto = 0.2
        self.timer_id = 0
        self.active_timer = None

    def record_tcp_state(self):
        # Record CWND and ssthresh
        self.cwnd_history.append({
            "time": self.current_time,
            "cwnd": self.tcp["cwnd"],
            "ssthresh": self.tcp["ssthresh"]
        })

        # Record only actual TCP state transitions
        current_state = self.tcp["state"]

        if self.state_history[-1]["state"] != current_state:
            self.state_history.append({
                "time": self.current_time,
                "state": current_state
            })


    def record_packet_event(self, event, packet_number=None, router_name=None):
        self.packet_events.append({
            "time": self.current_time,
            "event": event,
            "packet": packet_number,
            "router": router_name
        })

    def receive_at_destination(self, packet):
        sequence = packet.sequence_number
        # Store the received packet, including out-of-order packets
        if sequence >= self.expected_sequence:
            self.received_packets.add(sequence)
        # Advance while consecutive packets are available
        while self.expected_sequence in self.received_packets:
            self.expected_sequence += 1
        # Cumulative ACK: next expected sequence number
        ack_number = self.expected_sequence
        self.generated_acks.append(ack_number)
        self.delivered_packets += 1
        return ack_number

    def schedule_event(self, event_time, event_type, packet, target=None):
        event = (
            event_time,
            self.event_counter,
            event_type,
            packet,
            target
        )
        heapq.heappush(self.event_queue, event)
        self.event_counter += 1

    def start_retransmission_timer(self, sequence_number, start_time):
        self.timer_id += 1
        # Identify the currently active timer
        self.active_timer = (self.timer_id, sequence_number)
        # Schedule timeout event
        timeout_time = start_time + self.rto
        self.schedule_event(timeout_time,"TIMEOUT",sequence_number,self.timer_id)

    def get_next_event(self):
        if not self.event_queue:
            return None
        event = heapq.heappop(self.event_queue)
        event_time, event_id, event_type, packet, target = event
        self.current_time = event_time
        return event

    def send_packet(self, packet):
        # First link: Sender -> R1
        link = self.links[0]
        # Sender can transmit only when its link is available
        start_time = max(self.current_time, self.sender_link_available_time)
        packet.sent_time = start_time
        transmission_delay = link.calculate_transmission_delay(packet)
        propagation_delay = link.calculate_propagation_delay()
        arrival_time = (start_time + transmission_delay + propagation_delay)
        self.sender_link_available_time = (start_time + transmission_delay)
        self.schedule_event(arrival_time, "PACKET_ARRIVAL", packet, "R1")

    def send_ack(self, ack):
        # Reverse link: Receiver -> R3
        link = self.links[3]
        start_time = max(self.current_time, self.ack_link_available_time)
        transmission_delay = link.calculate_transmission_delay(ack)
        propagation_delay = link.calculate_propagation_delay()
        arrival_time = (start_time + transmission_delay + propagation_delay)
        self.ack_link_available_time = (start_time + transmission_delay)
        self.schedule_event(arrival_time, "ACK_ARRIVAL", ack, "R3_ACK")


    def send_available_packets(self):
        while (
            self.next_sequence <= self.total_packets
            and len(self.unacked_packets) < self.tcp["cwnd"]
        ):
            packet = Packet(self.next_sequence, self.packet_size)

            # Check whether this is the first outstanding packet
            start_timer = len(self.unacked_packets) == 0

            self.unacked_packets[self.next_sequence] = packet
            self.send_packet(packet)
            self.record_packet_event("transmitted", packet_number=self.next_sequence)
            # Start RTO timer for the oldest outstanding packet
            if start_timer:
                self.start_retransmission_timer(
                    self.next_sequence,
                    packet.sent_time
                )

            print(
                f"{self.current_time * 1000:.2f} ms: "
                f"Sender transmitted Packet {self.next_sequence} "
                f"(CWND = {self.tcp['cwnd']:.2f})"
            )

            self.next_sequence += 1

    def retransmit_packet(self, sequence_number):
        packet = self.unacked_packets.get(sequence_number)
        if packet is None:
            return
        # Create a new transmission attempt
        retransmitted_packet = Packet(sequence_number,self.packet_size)
        print(
            f"{self.current_time * 1000:.2f} ms: "
            f"Retransmitting Packet {sequence_number}"
        )
        self.send_packet(retransmitted_packet)
        self.record_packet_event("retransmitted",packet_number=sequence_number)

    def process_next_event(self):
        event = self.get_next_event()
        if event is None:
            return
        event_time, event_id, event_type, packet, target = event
        # ----------------------------------
        # 1. FORWARD PATH: DATA PACKETS
        # ----------------------------------
        if event_type == "PACKET_ARRIVAL":
            if target == "RECEIVER":
                ack_number = self.receive_at_destination(packet)
                self.record_packet_event(
                    "delivered",
                    packet_number=packet.sequence_number
                )
                print(
                    f"{self.current_time * 1000:.2f} ms: "
                    f"Packet {packet.sequence_number} "
                    f"reached Receiver -> ACK {ack_number} generated"
                )
                # Create and send the ACK
                ack = Acknowledgement(ack_number)
                self.send_ack(ack)
            else:
                router = next(
                    r for r in self.routers if r.name == target
                )
                accepted = router.receive_packet(
                    packet,
                    self.current_time
                )
                if not accepted:
                    self.record_packet_event(
                        "dropped",
                        packet_number=packet.sequence_number,
                        router_name=router.name
                    )
                    print(
                        f"{self.current_time * 1000:.2f} ms: "
                        f"Packet {packet.sequence_number} "
                        f"dropped at {router.name}"
                    )
                elif router.active_packet is None:
                    router.process_queue(self.current_time)
                    self.schedule_event(
                        router.busy_until,
                        "ROUTER_COMPLETE",
                        router.active_packet,
                        router.name
                    )
        # ----------------------------------
        # 2. FORWARD PATH: ROUTER COMPLETION
        # ----------------------------------
        elif event_type == "ROUTER_COMPLETE":
            router = next(
                r for r in self.routers if r.name == target
            )
            completed_packets = router.process_queue(
                self.current_time
            )
            router_index = self.routers.index(router)
            next_targets = ["R2", "R3", "RECEIVER"]
            for completed_packet in completed_packets:
                self.record_packet_event(
                    "forwarded",
                    packet_number=completed_packet.sequence_number,
                    router_name=router.name
                )
                next_target = next_targets[router_index]
                next_link = self.links[router_index + 1]
                arrival_time = (
                    self.current_time
                    + next_link.calculate_propagation_delay()
                )
                self.schedule_event(
                    arrival_time,
                    "PACKET_ARRIVAL",
                    completed_packet,
                    next_target
                )
            if router.active_packet is not None:
                self.schedule_event(
                    router.busy_until,
                    "ROUTER_COMPLETE",
                    router.active_packet,
                    router.name
                )
        # ----------------------------------
        # 3. REVERSE PATH: ACK ARRIVAL
        # ----------------------------------
        elif event_type == "ACK_ARRIVAL":
            if target == "SENDER":
                ack_number = packet.ack_number
                # New cumulative ACK
                if ack_number > self.tcp["last_ack"]:
                    # Identify newly acknowledged packets
                    acknowledged = [
                        seq for seq in self.unacked_packets
                        if seq < ack_number
                    ]
                    # Take an RTT sample before removing the packet
                    sampled_packet = self.unacked_packets.get(
                        ack_number - 1
                    )
                    if sampled_packet is not None:

                        rtt = self.current_time - sampled_packet.sent_time
                        self.rtt_samples.append(rtt)
                    # Remove acknowledged packets
                    for seq in acknowledged:
                        del self.unacked_packets[seq]

                    # Restart or invalidate the retransmission timer
                    if self.unacked_packets:
                        oldest_packet = min(self.unacked_packets.keys())

                        self.start_retransmission_timer(
                            oldest_packet,
                            self.current_time
                        )
                    else:
                        self.active_timer = None
                    # Update TCP state
                    self.tcp["last_ack"] = ack_number
                    self.tcp["dup_ack_count"] = 0
                    from tcp_reno import on_ack
                    on_ack(self.tcp)
                    self.record_tcp_state()     
                    print(
                        f"{self.current_time * 1000:.2f} ms: "
                        f"ACK {ack_number} reached Sender | "
                        f"CWND = {self.tcp['cwnd']:.2f} | "
                        f"State = {self.tcp['state']}"
                    )
                    # Send more packets if the window permits
                    self.send_available_packets()
                # Duplicate ACK
                elif ack_number == self.tcp["last_ack"]:

                    self.tcp["flight_size"] = len(self.unacked_packets)

                    from tcp_reno import on_duplicate_ack
                    on_duplicate_ack(self.tcp, ack_number)
                    self.record_tcp_state()
                    if self.tcp["retransmit"]:
                        self.retransmit_packet(ack_number)
                        self.tcp["retransmit"] = False

                    print(
                        f"{self.current_time * 1000:.2f} ms: "
                        f"Duplicate ACK {ack_number} | "
                        f"Count = {self.tcp['dup_ack_count']} | "
                        f"CWND = {self.tcp['cwnd']:.2f}"
                    )
            else:
                router = next(
                    r for r in self.ack_routers if r.name == target
                )
                accepted = router.receive_packet(
                    packet,
                    self.current_time
                )
                if not accepted:
                    print(
                        f"{self.current_time * 1000:.2f} ms: "
                        f"ACK dropped at {router.name}"
                    )
                elif router.active_packet is None:
                    router.process_queue(self.current_time)
                    self.schedule_event(
                        router.busy_until,
                        "ACK_ROUTER_COMPLETE",
                        router.active_packet,
                        router.name
                    )

        elif event_type == "TIMEOUT":
            sequence_number = packet
            event_timer_id = target

            # Ignore outdated timeout events
            if self.active_timer is None:
                return

            if event_timer_id != self.active_timer[0]:
                return

            # Check for outstanding packets
            if not self.unacked_packets:
                self.active_timer = None
                return

            # Find the oldest unacknowledged packet
            oldest_sequence = min(self.unacked_packets.keys())

            if sequence_number != oldest_sequence:
                return

            print(
                f"{self.current_time * 1000:.2f} ms: "
                f"RTO expired for Packet {oldest_sequence}"
            )

            # Apply TCP Reno timeout response
            from tcp_reno import on_timeout

            flight_size = len(self.unacked_packets)
            on_timeout(self.tcp, flight_size)
            self.record_tcp_state()

            print(
                f"{self.current_time * 1000:.2f} ms: "
                f"Timeout recovery | CWND = {self.tcp['cwnd']:.2f} | "
                f"ssthresh = {self.tcp['ssthresh']:.2f}"
            )

            # Retransmit the oldest unacknowledged packet
            self.retransmit_packet(oldest_sequence)

            # Reset the retransmission flag
            self.tcp["retransmit"] = False

            # Start a new timer for the retransmitted packet
            self.start_retransmission_timer(
                oldest_sequence,
                self.current_time
            )

        # ----------------------------------
        # 4. REVERSE PATH: ACK ROUTER COMPLETION
        # ----------------------------------
        elif event_type == "ACK_ROUTER_COMPLETE":
            router = next(
                r for r in self.ack_routers if r.name == target
            )
            completed_acks = router.process_queue(
                self.current_time
            )
            router_index = self.ack_routers.index(router)
            next_targets = ["R2_ACK", "R1_ACK", "SENDER"]
            # Reverse link indices: R3->R2, R2->R1, R1->Sender
            link_indices = [2, 1, 0]
            for ack in completed_acks:
                next_target = next_targets[router_index]
                next_link = self.links[link_indices[router_index]]
                arrival_time = (
                    self.current_time
                    + next_link.calculate_propagation_delay()
                )
                self.schedule_event(
                    arrival_time,
                    "ACK_ARRIVAL",
                    ack,
                    next_target
                )
            if router.active_packet is not None:
                self.schedule_event(
                    router.busy_until,
                    "ACK_ROUTER_COMPLETE",
                    router.active_packet,
                    router.name
                )

    def run(self):
        while self.event_queue:
            self.process_next_event()

    def start_transfer(self, total_packets=10):
        self.total_packets = total_packets
        self.send_available_packets()
        self.run()


# if __name__ == "__main__":

#     network = Network()

#     # Generate 10 packets
#     packets = [
#         Packet(i, 1500)
#         for i in range(1, 11)
#     ]

#     # Send all packets into the network
#     for packet in packets:
#         network.send_packet(packet)

#     # Run the forward-path simulation
#     network.run()

#     print("\nNETWORK SUMMARY")

#     for router in network.routers:
#         print(f"\n{router.name}")
#         print("Forwarded:", router.forwarded_packets)
#         print("Dropped:", router.dropped_packets)

#     print("\nDelivered packets:", network.delivered_packets)
#     print("Generated ACKs:", network.generated_acks)

if __name__ == "__main__":

    network = Network()

    network.start_transfer(50)

    # print("\nTCP SUMMARY")
    # print("Final CWND:", network.tcp["cwnd"])
    # print("TCP State:", network.tcp["state"])
    # print("Unacknowledged packet numbers:", sorted(network.unacked_packets.keys()))

    # print("\nRTT SAMPLES (ms)")

    # for rtt in network.rtt_samples:
    #     print(round(rtt * 1000, 2))

    # print("\nCWND HISTORY:")
    # print(network.cwnd_history)

    # print("\nTCP STATE HISTORY:")
    # print(network.state_history)

    # print("\nPACKET EVENTS:")
    # print(network.packet_events[:15])

    # print("\nTOTAL PACKET EVENTS:")
    # print(len(network.packet_events))

    from collections import Counter

    event_counts = Counter(
        event["event"] for event in network.packet_events
    )

    print("EVENT COUNTS:")
    print(event_counts)

    times = [
        event["time"] for event in network.packet_events
    ]

    print(
        "Timestamps in chronological order:",
        all(times[i] <= times[i + 1] for i in range(len(times) - 1))
    )