import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/eldercare_regions_enriched.csv")
    df["ElderVulnerabilityIndex"] = df["SVI"] * (df["PopulationOver65"] / 100)
    return df

df = load_data()

# Sidebar: Region selector
region = st.sidebar.selectbox("Select a County", df["County"] + ", " + df["State"])

# Filter selected region
selected = df[df["County"] + ", " + df["State"] == region].iloc[0]

# Title and region
st.title("S.A.G.E. – Sustainable Aging Governance Engine")
st.subheader("AI-powered tool for equitable eldercare resource allocation")
st.markdown(f"### 📍 Selected Region: **{region}**")

# Key indicators
col1, col2, col3, col4 = st.columns(4)
col1.metric("SVI", f"{selected['SVI']:.2f}")
col2.metric("Over 65 (%)", f"{selected['PopulationOver65']:.1f}%")
col3.metric("Infrastructure", f"{selected['InfrastructureScore']:.2f}")
col4.metric("Satisfaction", f"{selected['ElderSatisfaction']:.2f}")

# Recommendation logic
def recommend(row):
    if row["SVI"] > 0.75 and row["InfrastructureScore"] < 0.5:
        return "🚨 High Priority – Consider Immediate Investment"
    elif row["SVI"] > 0.5:
        return "⚠️ Moderate Priority – Monitor and Prepare"
    else:
        return "✅ Stable – Maintain Current Support"

st.markdown("### Recommendation")
st.success(recommend(selected))

# Simulate impact of funding
st.markdown("### Simulate Satisfaction Impact")
funding_increase = st.slider("Proposed Funding Increase (%)", 0, 100, 10)

def simulate_satisfaction(base, infra, funding):
    projected = base + funding * (1 - infra) * 0.0015
    return min(projected, 1.0)

new_satisfaction = simulate_satisfaction(
    selected["ElderSatisfaction"],
    selected["InfrastructureScore"],
    funding_increase
)

st.metric("Projected Satisfaction", f"{new_satisfaction:.2f}")

# Regional comparison chart
st.markdown("### Top 10 Counties by Elder Vulnerability")
cols = ["ElderVulnerabilityIndex", "InfrastructureScore", "ElderSatisfaction"]
fig, ax = plt.subplots()
df.sort_values("ElderVulnerabilityIndex", ascending=False).head(10).plot(
    kind="bar",
    x="County",
    y=cols,
    ax=ax
)
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

st.caption("Data source: CDC/ATSDR SVI 2022, U.S. Census Bureau")
