import streamlit as st
import pandas as pd
import json
import time
import uuid
import base64
from pathlib import Path
from datetime import datetime
import sys
import os

# Ensure src is in the python path for Streamlit module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.visualizations import plot_risk_distribution, plot_attack_categories, plot_shap_bars, plot_risk_breakdown
from src.ui.data_layer import load_soc_telemetry

st.set_page_config(page_title="SentinelAI : Behavioral Threat Detection Platform", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    st.markdown("""
    <style>
    /* User Specific Request: White Main Page, Black Sidebar */
    .stApp { background-color: #ffffff !important; }
    [data-testid="stSidebar"] { background-color: #0e1117 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 95%; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Metrics - Original Dark Boxes */
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; color: #2196F3 !important; line-height: 1.2; }
    div[data-testid="stMetricLabel"] { font-size: 1.05rem; color: #90A4AE !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    div[data-testid="stMetric"] { background: linear-gradient(145deg, #1e222d, #161923); border-radius: 10px; padding: 20px; border: 1px solid #2d303e; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4); margin-bottom: 10px; }
    
    /* Buttons */
    .stButton > button { border-radius: 8px; border: 1px solid #2196F3; color: #2196F3; background-color: rgba(33, 150, 243, 0.1); transition: all 0.3s ease; font-weight: 700; width: 100%; padding: 0.6rem 1rem; }
    .stButton > button:hover { background-color: #2196F3; color: #ffffff !important; box-shadow: 0 0 15px rgba(33, 150, 243, 0.5); transform: translateY(-1px); }
    
    /* Cards - Original Dark Boxes */
    .investigation-card { background: linear-gradient(145deg, #1e222d, #161923); border-radius: 10px; padding: 24px; border: 1px solid #2d303e; margin-bottom: 24px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); }
    .card-header { font-size: 1.3rem; font-weight: 800; color: #2196F3; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Typography on the White Main Page */
    h1, h2, h3 { color: #1e1e1e !important; font-family: 'Inter', sans-serif; }
    p { color: #424242 !important; line-height: 1.6; font-size: 1.05rem; }
    
    /* Typography inside Dark Boxes */
    .investigation-card p, .investigation-card h3 { color: #ECEFF1 !important; }
    div[data-testid="stMetric"] p, div[data-testid="stMetric"] h3 { color: #ECEFF1 !important; }
    
    /* Subtitle */
    .hero-subtitle { text-align: center; color: #607D8B !important; font-size: 1.1rem; max-width: 800px; margin: 0 auto 2rem auto; font-weight: 400; line-height: 1.5; }
    
    /* Summary Card */
    .summary-card { background: linear-gradient(to right, rgba(33,150,243,0.1), rgba(0,0,0,0)); border-left: 4px solid #2196F3; padding: 20px; border-radius: 4px; margin-bottom: 25px; }
    .summary-title { font-size: 1.4rem; font-weight: bold; color: #2196F3; margin-bottom: 15px; }
    .summary-card span { color: #424242 !important; }
    
    /* Pipeline Nodes - Original Dark Boxes */
    .pipeline-node { background: #1e222d; border: 1px solid #2196F3; border-radius: 8px; padding: 15px; margin: 10px auto; text-align: center; font-weight: bold; color: #ECEFF1 !important; width: 350px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .pipeline-arrow { text-align: center; color: #2196F3; font-size: 1.5rem; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)
inject_custom_css()

HISTORY_FILE = Path("data/execution_history.json")
def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    return []
def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f: json.dump(history, f)

if "pipeline_run" not in st.session_state:
    st.session_state.pipeline_run = False
if "run_summary" not in st.session_state:
    st.session_state.run_summary = None

if st.session_state.pipeline_run:
    df = load_soc_telemetry()
else:
    df = pd.DataFrame(columns=[
        "event_id", "timestamp", "user_id", "device_id", "country", "ip_address", "authentication_method",
        "Risk Level", "Risk Score", "Attack Classification", "Explanation", 
        "SHAP_Values", "Risk_Breakdown", "Triggered_Rules", "Recommended_Action", 
        "Executive Summary"
    ])

# Executive Hero Section
st.markdown("<h1 style='text-align: center; color: #2196F3 !important; margin-bottom: 0.5rem; font-weight: 800;'>🛡️ SentinelAI : Behavioral Threat Detection Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-subtitle'>SentinelAI detects anomalous authentication behavior using behavioral profiling, hybrid AI detection, explainable machine learning, and threat intelligence to assist SOC analysts in identifying enterprise cyber threats.</p>", unsafe_allow_html=True)

# --- Navigation Grouping ---
st.sidebar.markdown("### 🧭 Navigation")
page = st.sidebar.radio("Select View", [
    "📊 Executive Security Overview",
    "🚨 Threat Hunting",
    "🔍 Deep Investigation",
    "🏛️ System Architecture"
], label_visibility="collapsed")

page = page.split(" ", 1)[1]

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Scenario Engine")
scenario = st.sidebar.selectbox("Select Threat Scenario", [
    "Mixed Enterprise Attack", "Normal Activity", "Brute Force Attack", 
    "Impossible Travel", "Credential Stuffing", "Password Spray", 
    "Insider Threat", "Suspicious Device"
])

if st.sidebar.button("🚀 Execute AI Pipeline"):
    run_id = str(uuid.uuid4())[:8].upper()
    start_time = time.time()
    
    with st.status("Executing Enterprise SOC Pipeline...", expanded=True) as status:
        st.write("✓ Generating Synthetic Dataset...")
        time.sleep(0.5)
        
        from src.runtime.orchestrator import PipelineRunner
        runner = PipelineRunner()
        config = {"scenario": scenario, "num_events": 2500}
        
        st.write("✓ Performing Feature Engineering...")
        st.write("✓ Building Behavioral Profiles...")
        runner.run_phase2(config_overrides=config)
        
        st.write("✓ Running Isolation Forest...")
        st.write("✓ Executing Rule Engine...")
        runner.run_phase3(config_overrides=config)
        
        st.write("✓ Calculating Risk Fusion...")
        st.write("✓ Classifying Threats (XGBoost)...")
        runner.run_phase4(config_overrides=config)
        
        st.write("✓ Generating SHAP Explanations...")
        runner.run_phase5(config_overrides=config)
        
        duration = time.time() - start_time
        st.write("✓ Dashboard Updated")
        status.update(label=f"Pipeline Execution Complete ({duration:.2f}s)!", state="complete", expanded=False)
    
    st.cache_data.clear()
    new_df = load_soc_telemetry()
    
    avg_risk = new_df["Risk Score"].mean() if not new_df.empty else 0
    threat_cats = new_df[new_df["Attack Classification"] != "Normal Authentication"]["Attack Classification"].nunique() if not new_df.empty else 0
    
    history_entry = {
        "Run ID": run_id,
        "Scenario": scenario,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Execution Time (s)": round(duration, 2),
        "Events Processed": len(new_df),
        "Critical Alerts": len(new_df[new_df["Risk Level"] == "Critical"]) if not new_df.empty else 0,
        "High Alerts": len(new_df[new_df["Risk Level"] == "High"]) if not new_df.empty else 0,
        "Average Risk Score": round(avg_risk, 2),
        "Top Threat": new_df[new_df["Attack Classification"] != "Normal Authentication"]["Attack Classification"].mode()[0] if not new_df[new_df["Attack Classification"] != "Normal Authentication"].empty else "None",
        "Status": "SUCCESS"
    }
    history = load_history()
    history.insert(0, history_entry)
    history = history[:5]
    save_history(history)
    
    st.session_state.pipeline_run = True
    st.session_state.run_summary = history_entry
    st.rerun()

history = load_history()

# Professional Pipeline Summary Card
if st.session_state.run_summary:
    s = st.session_state.run_summary
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">✅ Pipeline Execution Successful</div>
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; font-size: 1.05rem;">
            <div style="margin-right: 15px;"><strong>Run ID:</strong> <span>{s['Run ID']}</span></div>
            <div style="margin-right: 15px;"><strong>Scenario:</strong> <span>{s['Scenario']}</span></div>
            <div style="margin-right: 15px;"><strong>Exec Time:</strong> <span>{s['Execution Time (s)']}s</span></div>
            <div style="margin-right: 15px;"><strong>Events:</strong> <span>{s['Events Processed']}</span></div>
            <div style="margin-right: 15px;"><strong>Critical Alerts:</strong> <span style="color:#D32F2F !important;">{s['Critical Alerts']}</span></div>
            <div style="margin-right: 15px;"><strong>Avg Risk:</strong> <span style="color:#F57C00 !important;">{s['Average Risk Score']}</span></div>
            <div><strong>Timestamp:</strong> <span>{s['Timestamp']}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Dismiss Summary"):
        st.session_state.run_summary = None
        st.rerun()

# ----------------- EXECUTIVE SECURITY OVERVIEW -----------------
if page == "Executive Security Overview":
    st.markdown("<h2 style='border-bottom: 1px solid #E0E0E0; padding-bottom: 10px;'>📊 Executive Security Overview</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events Analyzed", len(df) if not df.empty else 0)
    col2.metric("Critical Threats", len(df[df["Risk Level"] == "Critical"]) if not df.empty else 0)
    
    avg_risk = df["Risk Score"].mean() if not df.empty else 0
    col3.metric("Enterprise Risk Score", f"{avg_risk:.2f}")
    
    anomalies = df[df["Attack Classification"] != "Normal Authentication"]
    top_threat = anomalies["Attack Classification"].mode()[0] if not anomalies.empty else "None"
    col4.metric("Primary Threat Vector", top_threat)
    
    st.write("")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Anomalies", len(anomalies))
        top_country = anomalies["country"].mode()[0] if not anomalies.empty and "country" in anomalies else "N/A"
        c2.metric("Top Targeted Region", top_country)
        top_user = anomalies["user_id"].mode()[0] if not anomalies.empty and "user_id" in anomalies else "N/A"
        c3.metric("Most Targeted Entity (User ID)", top_user)
        
        st.write("")
        c1, c2 = st.columns([1, 1])
        with c1: st.plotly_chart(plot_risk_distribution(df), use_container_width=True)
        with c2: st.plotly_chart(plot_attack_categories(df), use_container_width=True)
    else:
        st.info("No telemetry available. Please execute the AI pipeline to generate insights.")
        
    st.markdown("<h3 style='margin-top: 3rem; margin-bottom: 1rem;'>📜 Pipeline Comparison</h3>", unsafe_allow_html=True)
    if history:
        display_history = [
            {
                "Run ID": h.get("Run ID", "N/A"), 
                "Scenario": h.get("Scenario", "N/A"), 
                "Exec Time": f"{h.get('Execution Time (s)', 0)}s", 
                "Critical Alerts": h.get("Critical Alerts", 0), 
                "High Alerts": h.get("High Alerts", 0), 
                "Avg Risk": h.get("Average Risk Score", 0),
                "Top Threat": h.get("Top Threat", "N/A"),
                "Status": "✅ SUCCESS" if h.get("Status", "") == "SUCCESS" else "❌ FAILED"
            }
            for h in history
        ]
        st.dataframe(pd.DataFrame(display_history), use_container_width=True, hide_index=True)
    else:
        st.info("No execution history available.")

# ----------------- THREAT HUNTING -----------------
elif page == "Threat Hunting":
    st.markdown("<h2 style='border-bottom: 1px solid #E0E0E0; padding-bottom: 10px;'>🚨 Threat Hunting Queue</h2>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 2rem;'>Filter, prioritize, and triage high-risk alerts before deep investigation.</p>", unsafe_allow_html=True)
    if not df.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            risk_filter = st.multiselect("Filter Risk Level", options=["Critical", "High", "Moderate", "Low"], default=["Critical", "High"])
        with c3:
            st.write("") # Alignment hack
            export_csv = st.download_button(
                label="📥 Export Queue (CSV)",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"threat_queue_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
            
        filtered_df = df[df["Risk Level"].isin(risk_filter)] if risk_filter else df
        
        def format_risk(x):
            if x == "Critical": return "🔴 Critical"
            if x == "High": return "🟠 High"
            if x == "Moderate": return "🟡 Moderate"
            return "🔵 Low"
            
        display_df = filtered_df[["event_id", "timestamp", "user_id", "device_id", "country", "Risk Level", "Risk Score", "Attack Classification", "authentication_method"]].copy()
        display_df["Severity"] = display_df["Risk Level"].apply(format_risk)
        display_df["Auth Type"] = display_df["authentication_method"]
        display_df = display_df.rename(columns={"Attack Classification": "Threat Context"})
        
        st.dataframe(
            display_df[["event_id", "Severity", "Risk Score", "timestamp", "user_id", "country", "Auth Type", "Threat Context"]].head(200),
            use_container_width=True, 
            hide_index=True,
            column_config={
                "event_id": st.column_config.TextColumn("Event ID", width="small"),
                "Severity": st.column_config.TextColumn("Severity", width="small"),
                "Risk Score": st.column_config.ProgressColumn("Risk Score", format="%.2f", min_value=0, max_value=100, width="medium"),
                "timestamp": st.column_config.DatetimeColumn("Timestamp", format="DD-MMM-YYYY HH:mm"),
                "user_id": st.column_config.TextColumn("User ID"),
                "country": st.column_config.TextColumn("Country"),
                "Auth Type": st.column_config.TextColumn("Auth Type"),
                "Threat Context": st.column_config.TextColumn("Threat Context", width="medium")
            }
        )
    else:
        st.warning("No alerts available. Please execute the AI pipeline.")

# ----------------- DEEP INVESTIGATION -----------------
elif page == "Deep Investigation":
    st.markdown("<h2 style='border-bottom: 1px solid #E0E0E0; padding-bottom: 10px;'>🔍 Deep Investigation Console</h2>", unsafe_allow_html=True)
    if not df.empty:
        event_ids = df["event_id"].tolist()
        
        col_sel, col_empty, col_btn = st.columns([2, 1, 1])
        with col_sel:
            selected_event = st.selectbox("Select Event ID to Investigate (Sorted by Risk)", event_ids[:100])
        
        event_data = df[df["event_id"] == selected_event].iloc[0]
        
        with col_btn:
            st.write("") # alignment
            st.download_button(
                label="📄 Export Report (JSON)",
                data=event_data.to_json(indent=4).encode('utf-8'),
                file_name=f"investigation_report_EVT{selected_event}.json",
                mime='application/json'
            )
            
        try:
            exp_dict = json.loads(event_data["Explanation"])
            tech_raw = exp_dict.get('Technical_Analysis', '')
            tech_dict = {}
            for line in tech_raw.split('\n'):
                if ":" in line:
                    k, v = line.split(":", 1)
                    tech_dict[k.strip()] = v.strip()
        except:
            exp_dict = {}
            tech_dict = {}
            
        st.markdown(f"""
        <div class="investigation-card">
            <div class="card-header">📝 Executive Summary</div>
            <p style='font-size: 1.15rem; font-weight: 500;'>{exp_dict.get("Executive_Summary", "No summary available.")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='investigation-card'><div class='card-header'>🔬 Technical Evidence</div>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("AI Confidence", tech_dict.get("Prediction Confidence", "N/A"))
        t2.metric("Stat Anomaly Score", tech_dict.get("Statistical Deviation Score", "N/A"))
        t3.metric("User ID", event_data.get("user_id", "N/A"))
        t4.metric("IP Address", event_data.get("ip_address", "N/A"))
        
        with st.expander("View Raw Feature Evidence (JSON)"):
            st.code(tech_dict.get("Input Feature Values", "N/A"), language="json")
        st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='investigation-card'><div class='card-header'>🧠 AI Decision & Risk Breakdown</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(plot_shap_bars(event_data["SHAP_Values"]), use_container_width=True)
        with c2: st.plotly_chart(plot_risk_breakdown(event_data["Risk_Breakdown"]), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='investigation-card'><div class='card-header'>⚡ Triggered Deterministic Rules</div>", unsafe_allow_html=True)
        try:
            rules = json.loads(event_data["Triggered_Rules"])
            if rules: st.dataframe(pd.DataFrame(rules), use_container_width=True, hide_index=True)
            else: st.markdown("<p style='color: #4CAF50 !important; font-weight: bold;'>No deterministic rules triggered for this event.</p>", unsafe_allow_html=True)
        except:
            st.write("Error parsing rules.")
        st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='investigation-card' style='border-left: 4px solid #F44336;'><div class='card-header' style='color: #F44336 !important; border-color: rgba(244, 67, 54, 0.2);'>🛡️ Recommended Action</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin: 0;'>{event_data['Recommended_Action']}</h3>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No data available. Execute pipeline first.")

# ----------------- SYSTEM ARCHITECTURE -----------------
elif page == "System Architecture":
    st.markdown("<h2 style='border-bottom: 1px solid #E0E0E0; padding-bottom: 10px;'>🏛️ System Architecture</h2>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 2rem;'>Understanding the multi-layered hybrid AI architecture.</p>", unsafe_allow_html=True)
    
    col_text, col_diagram = st.columns([1.2, 1])
    
    with col_text:
        st.markdown("""
        #### ⚙️ Component Responsibilities
        The engine processes data strictly sequentially to ensure maximum fidelity and explainability:
        
        *   **Synthetic Data Generation:** Bootstraps realistic baseline enterprise logs and injects precise threat scenarios.
        *   **Feature Engineering:** Extracts critical time-series and spatial characteristics (e.g. time since last login, distance).
        *   **Behavior Profiling:** Builds continuous mathematical baselines for users and devices.
        *   **Isolation Forest:** Unsupervised ML model identifying multi-dimensional spatial anomalies.
        *   **Rule Engine:** Deterministic SOC heuristics that flag known enterprise signatures.
        *   **Risk Fusion:** Normalizes inputs into an enterprise 0-100 risk score and fuses confidence.
        *   **XGBoost:** Supervised learning categorizes the specific threat context (e.g. Credential Stuffing).
        *   **SHAP (XAI):** Generates interpretable feature importance evidence for the SOC analyst.
        
        #### 🛠️ Technology Stack
        * **Frontend:** Streamlit, Plotly, Pandas
        * **AI/ML Layer:** XGBoost, Scikit-Learn (Isolation Forest), SHAP
        * **Data Layer:** PyArrow (Parquet), JSON
        * **Runtime Environment:** Python 3.10+
        
        #### 📂 Folder Organization
        * `src/ai/`: Core Intelligence (Detection, Classification, XAI)
        * `src/data/`: Data Generation & Loaders
        * `src/runtime/`: Pipeline Orchestrators
        * `src/ui/`: Streamlit Dashboard
        * `data/`: Parquet storage layer
        """)
        
    with col_diagram:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #1e222d, #161923); border-radius: 10px; padding: 24px; border: 1px solid #2d303e; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <h4 style='color: #2196F3; margin-bottom: 1.5rem;'>Pipeline Data Flow</h4>
            <div class="pipeline-node">Synthetic Data Generator</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node">Feature Engineering</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node">Behavior Profiling</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node" style="border-color: #FF9800; color: #FF9800 !important;">Isolation Forest (Unsupervised)</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node" style="border-color: #FF9800; color: #FF9800 !important;">Rule Engine (Deterministic)</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node" style="border-color: #F44336; color: #F44336 !important;">Risk Fusion Engine</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node" style="border-color: #9C27B0; color: #9C27B0 !important;">XGBoost Classification (Supervised)</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node" style="border-color: #4CAF50; color: #4CAF50 !important;">SHAP Explainability (XAI)</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-node" style="background: #2196F3; color: white !important;">SOC Dashboard</div>
        </div>
        """, unsafe_allow_html=True)
