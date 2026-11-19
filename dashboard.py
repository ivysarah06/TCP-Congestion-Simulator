import streamlit as st
from simulator import run_simulation
from metrics import calculate_all_metrics
import plotly.express as px
import pandas as pd

# ------------------------------------------------------------------
# Palette
# ------------------------------------------------------------------
BG = "#0C1226"        # page background
SURFACE = "#171D31"   # cards / panels
ACCENT = "#2F7BFF"    # primary accent
MUTED = "#898E9C"     # secondary text
LIGHT = "#F2F6FF"     # primary text

st.set_page_config(
    page_title="TCP Congestion Control Simulator",
    layout="wide",
)

# ------------------------------------------------------------------
# Global styling
# ------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; color: {LIGHT}; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ max-width: 1200px; padding-top: 2.5rem; padding-bottom: 4rem; }}

    html, body, p, li, label, span, div {{ color: {LIGHT}; }}
    h1, h2, h3, h4 {{ color: {LIGHT}; letter-spacing: 0.2px; }}

    /* Title block */
    .hero {{ text-align: center; padding: 1rem 0 2rem 0; }}
    .hero h1 {{ font-size: 2.6rem; font-weight: 700; margin: 0 0 0.6rem 0; }}
    .hero p {{ color: {MUTED}; font-size: 1.1rem; max-width: 640px; margin: 0 auto; }}
    .hero .bar {{ width: 72px; height: 4px; background: {ACCENT};
                  border-radius: 2px; margin: 1.2rem auto 0 auto; }}

    /* Main section headers */
    .section-title {{ font-size: 1.6rem; font-weight: 700; color: {LIGHT};
                      margin: 3rem 0 1.2rem 0; padding-left: 0.9rem;
                      border-left: 5px solid {ACCENT}; }}
    .sub-title {{ font-size: 1.2rem; font-weight: 600; color: {LIGHT};
                  margin: 2rem 0 0.8rem 0; }}
    .sub-title span {{ color: {ACCENT}; }}

    /* Router cards */
    .router-card {{ background: {SURFACE}; border: 1px solid {SURFACE};
                    border-top: 3px solid {MUTED}; border-radius: 10px;
                    padding: 1rem 1.1rem; height: 100%; }}
    .router-card.bottleneck {{ border-top-color: {ACCENT}; border-color: {ACCENT}; }}
    .router-card h4 {{ margin: 0 0 0.6rem 0; font-size: 1.05rem; color: {LIGHT}; }}
    .router-card .row {{ display: flex; justify-content: space-between;
                         font-size: 0.9rem; padding: 0.2rem 0; }}
    .router-card .row .k {{ color: {MUTED}; }}
    .router-card .row .v {{ color: {LIGHT}; font-weight: 600; }}
    .router-card .tag {{ display: inline-block; font-size: 0.75rem; margin-top: 0.6rem;
                         padding: 0.1rem 0.6rem; border-radius: 999px;
                         background: {ACCENT}; color: {LIGHT}; }}

    /* Metrics */
    div[data-testid="stMetric"] {{ background: {SURFACE}; border-radius: 10px;
                                   padding: 1rem 1.2rem;
                                   border-left: 4px solid {ACCENT}; }}
    div[data-testid="stMetricLabel"] p {{ color: {MUTED}; }}
    div[data-testid="stMetricValue"] {{ color: {LIGHT}; }}

    /* Inputs & buttons */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {{
        background-color: {SURFACE}; border-color: {MUTED}; }}
    .stButton > button {{ background: {ACCENT}; color: {LIGHT}; border: none;
                          border-radius: 8px; padding: 0.6rem 1.6rem;
                          font-weight: 600; width: 100%; }}
    .stButton > button:hover {{ background: {LIGHT}; color: {BG}; }}

    /* Panels, alerts, tables */
    .panel {{ background: {SURFACE}; border-radius: 10px; padding: 1.2rem 1.4rem;
              margin-bottom: 1rem; }}
    .panel p {{ margin: 0.4rem 0; line-height: 1.6; }}
    .panel b {{ color: {ACCENT}; }}
    div[data-testid="stAlert"] {{ background: {SURFACE}; border-left: 4px solid {ACCENT}; }}
    div[data-testid="stDataFrame"] {{ border: 1px solid {SURFACE}; border-radius: 8px; }}
    details {{ background: {SURFACE}; border-radius: 8px; border: none !important; }}
    hr {{ border-color: {SURFACE}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def subsection(title, letter=None):
    prefix = f"<span>{letter}.</span> " if letter else ""
    st.markdown(f'<div class="sub-title">{prefix}{title}</div>', unsafe_allow_html=True)


def panel(html):
    st.markdown(f'<div class="panel">{html}</div>', unsafe_allow_html=True)


def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(color=LIGHT),
        title=dict(font=dict(size=16, color=LIGHT)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=LIGHT)),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(gridcolor=BG, zerolinecolor=BG, linecolor=MUTED, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=BG, zerolinecolor=BG, linecolor=MUTED, tickfont=dict(color=MUTED))
    return fig


# ------------------------------------------------------------------
# Title and introduction
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>TCP Congestion Control Simulator</h1>
        <p>An interactive simulation of TCP Reno and network congestion behaviour.</p>
        <div class="bar"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 1. Network Configuration Overview
# ------------------------------------------------------------------
section("1. Network Configuration Overview")
subsection("Network Topology")

topology = f"""
digraph {{
    rankdir=LR;
    bgcolor="transparent";
    nodesep=0.5;
    ranksep=0.6;

    node [
        shape=box,
        style="rounded,filled",
        fillcolor="{SURFACE}",
        fontcolor="{LIGHT}",
        color="{MUTED}",
        fontname="Helvetica",
        width=0.9,
        height=0.6
    ];
    edge [color="{MUTED}"];

    Sender -> R1 -> R2 -> R3 -> R4 -> R5 -> Receiver;

    R2 [fillcolor="{ACCENT}", color="{LIGHT}", penwidth=2];
    R4 [fillcolor="{ACCENT}", color="{LIGHT}", penwidth=2];
}}
"""
st.graphviz_chart(topology, width="stretch")

st.caption("Highlighted routers (R2 and R4) are the bottleneck links of the network.")

subsection("Router and Link Configuration")

routers = [
    ("R1", 10, 10, 1, False),
    ("R2", 8, 4, 1, True),
    ("R3", 10, 10, 1, False),
    ("R4", 6, 3, 1, True),
    ("R5", 10, 10, 1, False),
]

cols = st.columns(5)
for col, (name, buf, rate, delay, bottleneck) in zip(cols, routers):
    cls = "router-card bottleneck" if bottleneck else "router-card"
    tag = '<span class="tag">Bottleneck</span>' if bottleneck else ""
    col.markdown(
        f"""
        <div class="{cls}">
            <h4>{name}</h4>
            <div class="row"><span class="k">Buffer</span><span class="v">{buf} packets</span></div>
            <div class="row"><span class="k">Rate</span><span class="v">{rate} Mbps</span></div>
            <div class="row"><span class="k">Delay</span><span class="v">{delay} ms</span></div>
            {tag}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------
# 2. Simulation Configuration
# ------------------------------------------------------------------
section("2. Simulation Configuration")

cfg_col, btn_col = st.columns([2, 1], vertical_alignment="bottom")
with cfg_col:
    total_packets = st.number_input(
        "Number of packets to simulate",
        min_value=10,
        max_value=500,
        value=50,
        step=10,
    )
with btn_col:
    run_clicked = st.button("Run Simulation")

if run_clicked:
    st.session_state.results = run_simulation(total_packets)
    st.success("Simulation completed successfully!")

# ------------------------------------------------------------------
# Results (only after a simulation has been run)
# ------------------------------------------------------------------
if "results" not in st.session_state:
    st.info("Set the number of packets and select Run Simulation to view results and analysis.")
    st.stop()

results = st.session_state.results
metrics = calculate_all_metrics(results)

# ------------------------------------------------------------------
# 3. Simulation Results
# ------------------------------------------------------------------
section("3. Simulation Results")

# --- Performance Overview
subsection("Performance Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Throughput", f"{metrics['throughput_mbps']:.4f} Mbps")
c2.metric("Packet Loss", f"{metrics['packet_loss_rate']:.2f}%")
c3.metric("Average RTT", f"{metrics['average_rtt_ms']:.2f} ms")
c4.metric("Completion Time", f"{metrics['completion_time']:.4f} s")

# --- Congestion Window Analysis
subsection("Congestion Window Analysis")
cwnd_df = pd.DataFrame(results["cwnd_history"])
cwnd_df["time"] = cwnd_df["time"] * 1000

fig = px.line(
    cwnd_df,
    x="time",
    y=["cwnd", "ssthresh"],
    labels={
        "time": "Simulation Time (ms)",
        "value": "Window Size (packets)",
        "variable": "TCP Parameter",
    },
    color_discrete_map={"cwnd": ACCENT, "ssthresh": LIGHT},
    title="TCP Reno: Congestion Window vs Time",
)
fig.update_traces(line=dict(width=2.5))
fig.for_each_trace(
    lambda t: t.update(line=dict(dash="dash", width=2)) if t.name == "ssthresh" else ()
)
st.plotly_chart(style_fig(fig), use_container_width=True)

# --- TCP State Timeline
subsection("TCP State Timeline")
state_df = pd.DataFrame(results["state_history"])
state_df["time"] = state_df["time"] * 1000
state_df["end_time"] = state_df["time"].shift(-1)
state_df["duration"] = state_df["end_time"] - state_df["time"]
# The final state continues until simulation completion
state_df.loc[state_df.index[-1], "end_time"] = results["completion_time"] * 1000
state_df.loc[state_df.index[-1], "duration"] = (
    state_df.loc[state_df.index[-1], "end_time"] - state_df.loc[state_df.index[-1], "time"]
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
        "Congestion Avoidance": LIGHT,
        "Fast Recovery": MUTED,
    },
    labels={
        "time": "Simulation Time (ms)",
        "duration": "Duration (ms)",
        "state": "TCP State",
    },
    title="TCP Reno State Transitions",
)
fig_state.update_yaxes(autorange="reversed")
st.plotly_chart(style_fig(fig_state), use_container_width=True)

# --- Packet Event Log
subsection("Packet Event Log")
events_df = pd.DataFrame(results["packet_events"])

e1, e2, e3 = st.columns(3)
e1.metric("Total Events", len(events_df))
e2.metric("Packet Drops", int((events_df["event"] == "dropped").sum()))
e3.metric("Retransmissions", int((events_df["event"] == "retransmitted").sum()))

events_df["time"] = events_df["time"] * 1000
events_df = events_df.rename(
    columns={"time": "Time (ms)", "event": "Event", "packet": "Packet", "router": "Router"}
)

event_filter = st.selectbox(
    "Filter Events",
    ["All Events", "Important Events", "Packet Drops", "Retransmissions", "Packet Delivery"],
)
if event_filter == "Important Events":
    events_df = events_df[events_df["Event"].isin(["dropped", "retransmitted"])]
elif event_filter == "Packet Drops":
    events_df = events_df[events_df["Event"] == "dropped"]
elif event_filter == "Retransmissions":
    events_df = events_df[events_df["Event"] == "retransmitted"]
elif event_filter == "Packet Delivery":
    events_df = events_df[events_df["Event"] == "delivered"]

# Newest events first
events_df = events_df.sort_values(by="Time (ms)", ascending=False)
st.dataframe(events_df, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------
# 4. Simulation Analysis
# ------------------------------------------------------------------
section("4. Simulation Analysis")

packet_events_df = pd.DataFrame(results["packet_events"])

# --- A. Congestion Trend
subsection("Congestion Trend", "A")
drop_events = packet_events_df[packet_events_df["event"] == "dropped"].copy()

if drop_events.empty:
    st.success("No packet drops occurred during this simulation.")
else:
    drop_events["time_ms"] = drop_events["time"] * 1000

    fig_drop = px.scatter(
        drop_events,
        x="time_ms",
        y="packet",
        color="router",
        hover_data=["packet", "router", "time_ms"],
        title="Packet Drops Over Simulation Time",
        labels={
            "time_ms": "Simulation Time (ms)",
            "packet": "Packet Number",
            "router": "Router",
        },
        color_discrete_sequence=[ACCENT, LIGHT, MUTED],
    )
    fig_drop.update_traces(marker=dict(size=11, symbol="x"))
    st.plotly_chart(style_fig(fig_drop), use_container_width=True)

    panel(
        f"<p>Total packet-drop events: <b>{len(drop_events)}</b></p>"
        f"<p>Packet drops occurred between <b>{drop_events['time_ms'].min():.2f} ms</b> "
        f"and <b>{drop_events['time_ms'].max():.2f} ms</b>.</p>"
        f"<p>The simulation recorded drops across "
        f"<b>{drop_events['router'].nunique()}</b> router(s).</p>"
    )

    with st.expander("View actual packet-drop timestamps"):
        st.dataframe(
            drop_events[["time", "time_ms", "packet", "router"]],
            use_container_width=True,
            hide_index=True,
        )

# --- B. TCP Recovery Behaviour
subsection("TCP Recovery Behaviour", "B")

fast_retransmit_events = packet_events_df[packet_events_df["event"] == "fast_retransmit"]
timeout_events = packet_events_df[packet_events_df["event"] == "timeout_recovery"]
retransmission_events = packet_events_df[packet_events_df["event"] == "retransmitted"]

fast_retransmit_count = len(fast_retransmit_events)
timeout_count = len(timeout_events)
retransmission_count = len(retransmission_events)

r1, r2, r3 = st.columns(3)
r1.metric("Total Retransmissions", retransmission_count)
r2.metric("Fast Retransmit Triggers", fast_retransmit_count)
r3.metric("Timeout Recovery Triggers", timeout_count)

fast_packets = fast_retransmit_events["packet"].dropna().tolist()
timeout_packets = timeout_events["packet"].dropna().tolist()
fast_text = ", ".join(str(int(p)) for p in fast_packets) if fast_packets else "None"
timeout_text = ", ".join(str(int(p)) for p in timeout_packets) if timeout_packets else "None"

st.write("")
panel(
    f"<p><b>Packets triggering Fast Retransmit:</b> {fast_text}</p>"
    f"<p><b>Packets triggering Timeout Recovery:</b> {timeout_text}</p>"
)

if retransmission_count == 0:
    st.success(
        "No retransmissions were required. "
        "All packets were transmitted without triggering loss recovery."
    )
else:
    lines = [
        f"<p>TCP performed <b>{retransmission_count}</b> retransmission "
        f"attempt(s) to recover from packet loss.</p>"
    ]
    if fast_retransmit_count > 0:
        lines.append(
            f"<p>Fast Retransmit was triggered <b>{fast_retransmit_count}</b> time(s), "
            f"allowing TCP to respond to packet loss without waiting for a timeout.</p>"
        )
    if timeout_count > 0:
        lines.append(
            f"<p>Timeout Recovery was triggered <b>{timeout_count}</b> time(s), "
            f"indicating that some packet losses were detected through "
            f"retransmission timer expiration.</p>"
        )
    panel("".join(lines))

# --- C. Overall TCP Congestion Control Interpretation
subsection("Overall TCP Congestion Control Interpretation", "C")

cwnd_history = results["cwnd_history"]
state_history = results["state_history"]

# Normalise state names so both "Slow Start" and "SLOW_START" are counted
states = [entry["state"].upper().replace(" ", "_") for entry in state_history]
state_counts = pd.Series(states).value_counts().to_dict()

slow_start_count = state_counts.get("SLOW_START", 0)
congestion_avoidance_count = state_counts.get("CONGESTION_AVOIDANCE", 0)
fast_recovery_count = state_counts.get("FAST_RECOVERY", 0)

html = (
    f"<p><b>Congestion-control phases:</b> TCP spent "
    f"{slow_start_count} recorded intervals in Slow Start, "
    f"{congestion_avoidance_count} in Congestion Avoidance, "
    f"and {fast_recovery_count} in Fast Recovery.</p>"
    f"<p><b>Congestion response:</b> Fast Retransmit was triggered "
    f"{fast_retransmit_count} time(s), while Timeout Recovery was triggered "
    f"{timeout_count} time(s). These mechanisms allow TCP Reno to detect "
    f"packet loss and adjust its sending behaviour.</p>"
)

if len(cwnd_history) >= 2:
    initial_cwnd = cwnd_history[0]["cwnd"]
    final_cwnd = cwnd_history[-1]["cwnd"]
    maximum_cwnd = max(entry["cwnd"] for entry in cwnd_history)
    html += (
        f"<p><b>Congestion window behaviour:</b> CWND started at "
        f"{initial_cwnd} packets, reached a maximum of {maximum_cwnd} packets, "
        f"and ended at {final_cwnd} packets.</p>"
    )

html += (
    "<p><b>Overall interpretation:</b> The simulation illustrates TCP Reno's "
    "congestion-control process: increasing CWND to utilize available network "
    "capacity, detecting congestion through loss signals, and adjusting its "
    "sending rate through recovery mechanisms. The CWND graph and state timeline "
    "show how these mechanisms influence TCP's transmission behaviour.</p>"
)
panel(html)