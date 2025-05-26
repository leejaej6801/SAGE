# sage_demo_app.py

import streamlit as st
import numpy as np

# Title and intro
st.title("S.A.G.E. - Sustainable Aging Governance Engine")
st.subheader("AI-powered tool for equitable eldercare resource allocation")

st.markdown("""
This demo simulates how S.A.G.E. allocates resources based on budget, local needs, and priority settings. It reflects data-driven prioritization for underserved elderly populations.
""")

# Input Section
st.header("Input Parameters")

budget = st.number_input("Available Budget (in USD)", min_value=10000, step=10000, value=500000)
region_type = st.selectbox("Region Type", ["Urban", "Rural", "Mixed"])
underinvestment_level = st.slider("Underinvestment Level (0: Well-Served, 100: Severely Under-Served)", 0, 100, 50)
elder_satisfaction = st.slider("Current Elder Satisfaction (0: Very Low, 100: Very High)", 0, 100, 40)
infrastructure_score = st.slider("Infrastructure Quality (0: Poor, 100: Excellent)", 0, 100, 30)

st.subheader("Priority Weights")
health_priority = st.slider("Health Outcomes Priority", 0, 100, 70)
equity_priority = st.slider("Racial/Socioeconomic Equity Priority", 0, 100, 80)
digital_access_priority = st.slider("Digital Inclusion Priority", 0, 100, 50)

# Processing Section
st.header("Optimized Resource Allocation")

# Basic simulation logic (can be replaced by advanced optimization)
# Weighted allocation: more funds to areas with higher priority and lower infrastructure
total_priority = health_priority + equity_priority + digital_access_priority
health_alloc = (health_priority / total_priority) * (100 - infrastructure_score) / 100
equity_alloc = (equity_priority / total_priority) * (100 - elder_satisfaction) / 100
digital_alloc = (digital_access_priority / total_priority) * (100 - underinvestment_level) / 100

# Normalize allocations to sum to 1
alloc_sum = health_alloc + equity_alloc + digital_alloc
health_alloc_norm = health_alloc / alloc_sum
equity_alloc_norm = equity_alloc / alloc_sum
digital_alloc_norm = digital_alloc / alloc_sum

# Budget allocation
health_budget = budget * health_alloc_norm
equity_budget = budget * equity_alloc_norm
digital_budget = budget * digital_alloc_norm

# Display results
st.write(f"**Health Services Allocation:** ${health_budget:,.2f} ({health_alloc_norm * 100:.1f}%)")
st.write(f"**Equity-Focused Programs:** ${equity_budget:,.2f} ({equity_alloc_norm * 100:.1f}%)")
st.write(f"**Digital Access & Telehealth:** ${digital_budget:,.2f} ({digital_alloc_norm * 100:.1f}%)")

# AI Explanation (mock)
st.header("AI Policy Assistant Explanation")
explanation = f"""
Based on your input parameters, the model prioritizes health outcomes and racial/socioeconomic equity due to the region’s moderate infrastructure score and low elder satisfaction. 
A significant portion of the budget is allocated to health services to address critical care gaps, while a substantial share is directed toward equity-focused initiatives to mitigate systemic disparities. 
Digital inclusion receives proportionally less emphasis, reflecting the current underinvestment level and infrastructure capacity.
"""
st.write(explanation)
# src/app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
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

# App title
st.title("S.A.G.E. – Sustainable Aging Governance Engine")
st.subheader(f"📍 {region}")

# Show key metrics
st.markdown("### Key Indicators")
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

# Comparison chart
st.markdown("### Regional Comparison")
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


