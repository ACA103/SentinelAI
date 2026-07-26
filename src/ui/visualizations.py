import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

def plot_risk_distribution(df: pd.DataFrame):
    fig = px.histogram(df, x="Risk Score", nbins=50, color_discrete_sequence=["#2196F3"])
    fig.update_layout(
        title=dict(text="Risk Score Distribution", font=dict(color="#ECEFF1", size=18)),
        xaxis_title=dict(text="Risk Score", font=dict(color="#B0BEC5")),
        yaxis_title=dict(text="Event Count", font=dict(color="#B0BEC5")),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(color="#B0BEC5")
    )
    return fig

def plot_attack_categories(df: pd.DataFrame):
    counts = df["Attack Classification"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    fig = px.pie(
        counts, 
        names="Category", 
        values="Count", 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Tealgrn
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title=dict(text="Threat Context Distribution", font=dict(color="#ECEFF1", size=18)),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color="#B0BEC5"))
    )
    return fig

def plot_shap_bars(shap_json: str):
    try:
        data = json.loads(shap_json)
        if not data:
            return go.Figure()
        df = pd.DataFrame(data).sort_values("contribution", ascending=True)
        fig = px.bar(df, x="contribution", y="feature", orientation='h', color_discrete_sequence=["#9C27B0"])
        fig.update_layout(
            title=dict(text="AI Explainability (SHAP)", font=dict(color="#ECEFF1", size=16)),
            xaxis_title=dict(text="Contribution Impact", font=dict(color="#B0BEC5")),
            yaxis_title="",
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=20, t=40, b=30),
            font=dict(color="#B0BEC5")
        )
        return fig
    except:
        return go.Figure()

def plot_risk_breakdown(risk_json: str):
    try:
        data = json.loads(risk_json)
        # Filter out final risk score to just show the additive components
        components = {k: v for k, v in data.items() if "Contribution" in k and k != "Final Risk Score"}
        
        fig = px.pie(
            names=list(components.keys()), 
            values=list(components.values()), 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textinfo='value+label', textposition='inside')
        fig.update_layout(
            title=dict(text="Risk Fusion Breakdown", font=dict(color="#ECEFF1", size=16)),
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        return fig
    except:
        return go.Figure()
