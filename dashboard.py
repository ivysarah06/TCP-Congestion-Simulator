# import streamlit as st
# from simulator import run_simulation
# from metrics import calculate_all_metrics
# import plotly.express as px
# import pandas as pd

# st.title("TCP Congestion Control Simulator")

# st.write(
#     "An interactive simulation of TCP Reno "
#     "and network congestion behaviour."
# )

# st.header("Simulation Configuration")
# st.header("Network Configuration Overview")

# st.subheader("Network Topology")
# topology = """
# digraph {
#     rankdir=LR;
#     node [shape=box, style="rounded,filled",
#           fillcolor="#E0E7FF", color="#64748B"];
#     Sender -> R1 -> R2 -> R3 -> Receiver;
#     R2 [fillcolor="#FEE2E2", color="#DC2626",
#         penwidth=2];
# }
# """
# st.graphviz_chart(topology, use_container_width=True)

# st.subheader("Network Parameters")
# total_packets = st.number_input(
#     "Number of packets to simulate",
#     min_value=10,
#     max_value=500,
#     value=50,
#     step=10
# )
# if st.button("Run Simulation"):
#     st.session_state.results = run_simulation(total_packets)
#     st.success("Simulation completed successfully!")

# if "results" in st.session_state:
#     results = st.session_state.results
    
#     metrics = calculate_all_metrics(results)
#     st.header("Performance Overview")
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Throughput", f"{metrics['throughput_mbps']:.4f} Mbps")
#     col2.metric("Packet Loss", f"{metrics['packet_loss_rate']:.2f}%")
#     col3.metric("Average RTT", f"{metrics['average_rtt_ms']:.2f} ms")
#     col4.metric("Completion Time", f"{metrics['completion_time']:.4f} s")

#     st.header("Congestion Window Analysis")
#     # Convert CWND history into a Pandas DataFrame
#     cwnd_df = pd.DataFrame(results["cwnd_history"])
#     # Convert simulation time from seconds to milliseconds
#     cwnd_df["time"] = cwnd_df["time"] * 1000
#     # Create the CWND and SSThresh line graph
#     fig = px.line(
#         cwnd_df,
#         x="time",
#         y=["cwnd", "ssthresh"],
#         labels={
#             "time": "Simulation Time (ms)",
#             "value": "Window Size (packets)",
#             "variable": "TCP Parameter"
#         },
#         color_discrete_map={
#             "cwnd": "#2563EB",
#             "ssthresh": "#F59E0B"
#         },
#         title="TCP Reno: Congestion Window vs Time"
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     st.subheader("TCP State Timeline")
#     state_df = pd.DataFrame(results["state_history"])
#     # Convert time from seconds to milliseconds
#     state_df["time"] = state_df["time"] * 1000
#     # Determine when each state ends
#     state_df["end_time"] = state_df["time"].shift(-1)
#     state_df["duration"] = (state_df["end_time"] - state_df["time"])
#     # The final state continues until simulation completion
#     state_df.loc[state_df.index[-1], "end_time"] = (
#         results["completion_time"] * 1000
#     )
#     fig_state = px.bar(
#         state_df,
#         x="duration",
#         y="state",
#         orientation="h",
#         base="time",
#         color="state",
#         color_discrete_map={
#             "Slow Start": "#2563EB",
#             "Congestion Avoidance": "#16A34A",
#             "Fast Recovery": "#D97706"
#         },
#         labels={
#             "time": "Simulation Time (ms)",
#             "duration": "Duration (ms)",
#             "state": "TCP State"
#         },
#         title="TCP Reno State Transitions"
#     )
#     fig_state.update_yaxes(autorange="reversed")
#     st.plotly_chart(fig_state, use_container_width=True)

#     st.header("Packet Event Log")
#     events_df = pd.DataFrame(results["packet_events"])
#     total_events = len(events_df)
#     packet_drops = (events_df["event"] == "dropped").sum()
#     retransmissions = (events_df["event"] == "retransmitted").sum()
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Events", total_events)
#     col2.metric("Packet Drops", packet_drops)
#     col3.metric("Retransmissions", retransmissions)
#     events_df["time"] = events_df["time"] * 1000
#     events_df = events_df.rename(columns={
#         "time": "Time (ms)",
#         "event": "Event",
#         "packet": "Packet",
#         "router": "Router"
#     })
#     event_filter = st.selectbox(
#         "Filter Events",
#         [
#             "All Events",
#             "Important Events",
#             "Packet Drops",
#             "Retransmissions",
#             "Packet Delivery"
#         ]
#     )
#     if event_filter == "Important Events":
#         events_df = events_df[
#             events_df["Event"].isin(
#                 ["dropped", "retransmitted"]
#             )
#         ]
#     elif event_filter == "Packet Drops":
#         events_df = events_df[
#             events_df["Event"] == "dropped"
#         ]
#     elif event_filter == "Retransmissions":
#         events_df = events_df[
#             events_df["Event"] == "retransmitted"
#         ]
#     elif event_filter == "Packet Delivery":
#         events_df = events_df[
#             events_df["Event"] == "delivered"
#         ]
#     events_df = events_df.sort_values(
#         by="Time (ms)",
#         ascending=False
#     )
#     st.dataframe(
#         events_df,
#         use_container_width=True,
#         hide_index=True
#     )
#     # Display newest events first
#     events_df = events_df.sort_values(by="Time (ms)",ascending=False)

# st.header("Simulation Analysis")




import streamlit as st
from simulator import run_simulation
from metrics import calculate_all_metrics
import plotly.express as px
import pandas as pd

# ------------------------------------------------------------------
# Palette
# ------------------------------------------------------------------
BG = "#0C1226"        # page background
CARD = "#171D31"      # cards / panels
ACCENT = "#2F7BFF"    # primary accent
MUTED = "#898E9C"     # secondary text / borders
TEXT = "#F2F6FF"      # primary text

st.set_page_config(
    page_title="TCP Congestion Control Simulator",
    layout="wide"
)

# ------------------------------------------------------------------
# Global styling (display only)
# ------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}
    header[data-testid="stHeader"] {{
        background-color: {BG};
    }}
    .block-container {{
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    /* Typography */
    h1 {{
        color: {TEXT};
        font-weight: 800;
        letter-spacing: -0.5px;
        border-bottom: 3px solid {ACCENT};
        padding-bottom: 0.4rem;
        margin-bottom: 0.8rem;
    }}
    h2 {{
        color: {TEXT};
        font-weight: 700;
        border-left: 5px solid {ACCENT};
        padding-left: 0.7rem;
        margin-top: 2rem;
    }}
    h3 {{
        color: {ACCENT};
        font-weight: 600;
    }}
    p, label, li, span {{
        color: {TEXT};
    }}
    [data-testid="stCaptionContainer"], .stMarkdown small {{
        color: {MUTED};
    }}

    /* Intro text */
    .intro {{
        color: {MUTED};
        font-size: 1.1rem;
        margin-bottom: 1.2rem;
    }}

    /* Panels */
    .panel {{
        background-color: {CARD};
        border: 1px solid {MUTED}55;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
    }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid {MUTED}55;
        border-top: 3px solid {ACCENT};
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }}
    div[data-testid="stMetricLabel"] p {{
        color: {MUTED};
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    div[data-testid="stMetricValue"] {{
        color: {TEXT};
        font-weight: 700;
    }}

    /* Inputs */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {{
        background-color: {CARD};
        border-color: {MUTED}88;
        color: {TEXT};
    }}
    div[data-baseweb="input"] input {{
        color: {TEXT};
    }}
    div[data-testid="stNumberInput"] button {{
        background-color: {CARD};
        color: {TEXT};
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {ACCENT};
        color: {TEXT};
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: {TEXT};
        color: {BG};
        box-shadow: 0 0 0 3px {ACCENT}66;
    }}

    /* Alerts */
    div[data-testid="stAlert"] {{
        background-color: {CARD};
        border: 1px solid {ACCENT};
        border-radius: 10px;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        color: {MUTED};
        font-weight: 600;
        font-size: 1rem;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {TEXT};
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: {ACCENT};
    }}
    div[data-baseweb="tab-border"] {{
        background-color: {MUTED}55;
    }}

    /* Dataframe */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {MUTED}55;
        border-radius: 10px;
        overflow: hidden;
    }}

    hr {{
        border-color: {MUTED}55;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


def style_figure(fig):
    """Apply the dark palette to a Plotly figure (display only)."""
    fig.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=TEXT),
        title_font=dict(color=TEXT, size=18),
        legend=dict(
            bgcolor=CARD,
            bordercolor=MUTED,
            font=dict(color=TEXT)
        ),
        margin=dict(l=40, r=30, t=70, b=40)
    )
    fig.update_xaxes(
        gridcolor=MUTED + "33",
        linecolor=MUTED,
        zerolinecolor=MUTED + "55",
        tickfont=dict(color=MUTED),
        title_font=dict(color=TEXT)
    )
    fig.update_yaxes(
        gridcolor=MUTED + "33",
        linecolor=MUTED,
        zerolinecolor=MUTED + "55",
        tickfont=dict(color=MUTED),
        title_font=dict(color=TEXT)
    )
    return fig


# ------------------------------------------------------------------
# Header / Introduction
# ------------------------------------------------------------------
st.title("TCP Congestion Control Simulator")

st.markdown(
    '<p class="intro">An interactive simulation of TCP Reno '
    'and network congestion behaviour.</p>',
    unsafe_allow_html=True
)

# ------------------------------------------------------------------
# Network Topology (below introduction, above configuration)
# ------------------------------------------------------------------
st.header("Network Configuration Overview")

st.subheader("Network Topology")
topology = f"""
digraph {{
    bgcolor="transparent";
    rankdir=LR;
    node [shape=box, style="rounded,filled",
          fillcolor="{CARD}", color="{MUTED}",
          fontcolor="{TEXT}", fontname="Helvetica"];
    edge [color="{MUTED}", penwidth=1.5];
    Sender -> R1 -> R2 -> R3 -> Receiver;
    R2 [fillcolor="{ACCENT}", color="{TEXT}",
        fontcolor="{TEXT}", penwidth=2];
}}
"""
st.graphviz_chart(topology, use_container_width=True)

# ------------------------------------------------------------------
# Simulation Configuration
# ------------------------------------------------------------------
st.header("Simulation Configuration")

st.subheader("Network Parameters")
total_packets = st.number_input(
    "Number of packets to simulate",
    min_value=10,
    max_value=500,
    value=50,
    step=10
)
if st.button("Run Simulation"):
    st.session_state.results = run_simulation(total_packets)
    st.success("Simulation completed successfully!")

# ------------------------------------------------------------------
# Results (everything under Run Simulation)
# ------------------------------------------------------------------
if "results" in st.session_state:
    results = st.session_state.results

    metrics = calculate_all_metrics(results)

    st.markdown("---")
    st.header("Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Throughput", f"{metrics['throughput_mbps']:.4f} Mbps")
    col2.metric("Packet Loss", f"{metrics['packet_loss_rate']:.2f}%")
    col3.metric("Average RTT", f"{metrics['average_rtt_ms']:.2f} ms")
    col4.metric("Completion Time", f"{metrics['completion_time']:.4f} s")

    tab_cwnd, tab_state, tab_log = st.tabs([
        "Congestion Window Analysis",
        "TCP State Timeline",
        "Packet Event Log"
    ])

    # ---------------- Congestion Window ----------------
    with tab_cwnd:
        st.header("Congestion Window Analysis")
        # Convert CWND history into a Pandas DataFrame
        cwnd_df = pd.DataFrame(results["cwnd_history"])
        # Convert simulation time from seconds to milliseconds
        cwnd_df["time"] = cwnd_df["time"] * 1000
        # Create the CWND and SSThresh line graph
        fig = px.line(
            cwnd_df,
            x="time",
            y=["cwnd", "ssthresh"],
            labels={
                "time": "Simulation Time (ms)",
                "value": "Window Size (packets)",
                "variable": "TCP Parameter"
            },
            color_discrete_map={
                "cwnd": ACCENT,
                "ssthresh": TEXT
            },
            title="TCP Reno: Congestion Window vs Time"
        )
        st.plotly_chart(style_figure(fig), use_container_width=True)

    # ---------------- TCP State Timeline ----------------
    with tab_state:
        st.header("TCP State Timeline")
        state_df = pd.DataFrame(results["state_history"])
        # Convert time from seconds to milliseconds
        state_df["time"] = state_df["time"] * 1000
        # Determine when each state ends
        state_df["end_time"] = state_df["time"].shift(-1)
        state_df["duration"] = (state_df["end_time"] - state_df["time"])
        # The final state continues until simulation completion
        state_df.loc[state_df.index[-1], "end_time"] = (
            results["completion_time"] * 1000
        )
        fig_state = px.bar(
            state_df,
            x="duration",
            y="state",
            orientation="h",
            base="time",
            color="state",
            color_discrete_map={
                "Slow Start": ACCENT,
                "Congestion Avoidance": TEXT,
                "Fast Recovery": MUTED
            },
            labels={
                "time": "Simulation Time (ms)",
                "duration": "Duration (ms)",
                "state": "TCP State"
            },
            title="TCP Reno State Transitions"
        )
        fig_state.update_yaxes(autorange="reversed")
        st.plotly_chart(style_figure(fig_state), use_container_width=True)

    # ---------------- Packet Event Log ----------------
    with tab_log:
        st.header("Packet Event Log")
        events_df = pd.DataFrame(results["packet_events"])
        total_events = len(events_df)
        packet_drops = (events_df["event"] == "dropped").sum()
        retransmissions = (events_df["event"] == "retransmitted").sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Events", total_events)
        col2.metric("Packet Drops", packet_drops)
        col3.metric("Retransmissions", retransmissions)
        events_df["time"] = events_df["time"] * 1000
        events_df = events_df.rename(columns={
            "time": "Time (ms)",
            "event": "Event",
            "packet": "Packet",
            "router": "Router"
        })
        event_filter = st.selectbox(
            "Filter Events",
            [
                "All Events",
                "Important Events",
                "Packet Drops",
                "Retransmissions",
                "Packet Delivery"
            ]
        )
        if event_filter == "Important Events":
            events_df = events_df[
                events_df["Event"].isin(
                    ["dropped", "retransmitted"]
                )
            ]
        elif event_filter == "Packet Drops":
            events_df = events_df[
                events_df["Event"] == "dropped"
            ]
        elif event_filter == "Retransmissions":
            events_df = events_df[
                events_df["Event"] == "retransmitted"
            ]
        elif event_filter == "Packet Delivery":
            events_df = events_df[
                events_df["Event"] == "delivered"
            ]
        events_df = events_df.sort_values(
            by="Time (ms)",
            ascending=False
        )
        st.dataframe(
            events_df,
            use_container_width=True,
            hide_index=True
        )
        # Display newest events first
        events_df = events_df.sort_values(by="Time (ms)", ascending=False)

st.header("Simulation Analysis")