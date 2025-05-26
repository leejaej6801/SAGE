import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/Eldercare_Regional_Dataset.csv")
    df["ElderVulnerabilityIndex"] = df["SVI"] * (df["PopulationOver65"] / 100)
    return df

df = load_data()

# Page navigation
page = st.sidebar.radio("Navigate", ["Welcome", "County Explorer", "National Summary", "Simulation Tool (Coming Soon)"])

# Welcome Page
if page == "Welcome":
    st.title("S.A.G.E. – Sustainable Aging Governance Engine")
    st.subheader("AI-powered tool for equitable eldercare resource allocation")
    st.markdown("""
    Welcome to S.A.G.E., a decision intelligence tool that helps local governments identify and prioritize regions
    for eldercare investment. This platform integrates social vulnerability data, aging demographics, and predictive
    modeling to help allocate resources where they will have the greatest impact.

    **Key Decision-Making Factors:**
    - **SVI (Social Vulnerability Index):** How structurally disadvantaged is the region?
    - **Population Over 65 (%):** What proportion of the population is elderly?
    - **Infrastructure Score:** How well-prepared is the region to support eldercare?
    - **Projected Satisfaction Impact:** What return could we expect on additional investment?
    
    Use the sidebar to explore real data and simulate decisions.
    """)

# County Explorer Page
elif page == "County Explorer":
    st.title("Explore County Vulnerability and Aging Data")

    selected_state = st.selectbox("Select a State", sorted(df["State"].unique()))
    filtered_df = df[df["State"] == selected_state]

    selected_county = st.selectbox("Select a County", filtered_df["County"])
    selected_row = filtered_df[filtered_df["County"] == selected_county].iloc[0]

    st.markdown(f"### {selected_county}, {selected_row['State']}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("SVI", f"{selected_row['SVI']:.2f}")
    col2.metric("Over 65 (%)", f"{selected_row['PopulationOver65']:.1f}%")
    col3.metric("Infrastructure", f"{selected_row['InfrastructureScore']:.2f}")
    col4.metric("Satisfaction", f"{selected_row['ElderSatisfaction']:.2f}")

    def recommend(row):
        if row["SVI"] > 0.75 and row["InfrastructureScore"] < 0.5:
            return "High Priority – Consider Immediate Investment"
        elif row["SVI"] > 0.5:
            return "Moderate Priority – Monitor and Prepare"
        else:
            return "Stable – Maintain Current Support"

    st.markdown("### Recommendation")
    st.success(recommend(selected_row))

    st.markdown("### Top 10 Counties by Vulnerability (within selected state)")
    top_10 = filtered_df.sort_values("ElderVulnerabilityIndex", ascending=False).head(10)
    st.dataframe(top_10[["County", "SVI", "PopulationOver65", "ElderVulnerabilityIndex"]].reset_index(drop=True))

# National Summary Page
elif page == "National Summary":
    st.title("National Summary of Eldercare Vulnerability")

    st.markdown("#### Top 10 Most Vulnerable Counties (Nationwide)")
    top_counties = df.sort_values("ElderVulnerabilityIndex", ascending=False).head(10)
    st.dataframe(top_counties[["County", "State", "SVI", "PopulationOver65", "ElderVulnerabilityIndex"]].reset_index(drop=True))

    st.markdown("#### Top 10 States by Average Vulnerability")
    state_avg = df.groupby("State")["ElderVulnerabilityIndex"].mean().sort_values(ascending=False).head(10)
    st.dataframe(state_avg.reset_index().rename(columns={"ElderVulnerabilityIndex": "Avg Elder Vulnerability Index"}))

    st.markdown("#### Ideas for Further Analysis")
    st.markdown("""
    - Identify geographic clusters of high vulnerability
    - Highlight states with high variability (some counties low, others extremely high)
    - Compare average SVI to average infrastructure score per state
    - Flag counties with high elder population but low infrastructure scores as under-resourced
    - Visualize vulnerability vs satisfaction to identify underperformers
    """)

# Simulation Tool Placeholder
elif page == "Simulation Tool (Coming Soon)":
    st.title("Decision Simulation Tool")
    st.info("This module will allow you to test investment scenarios and forecast the efficiency of resource allocation.")

    st.markdown("""
    ### Preview: Investment Impact Model
    This tool will estimate the projected improvement in elder satisfaction given a proposed budget increase and existing infrastructure score.

    We'll use a basic regression model trained on historical patterns (e.g., where increased spending led to higher satisfaction outcomes).

    Core variables to include:
    - Baseline elder satisfaction
    - Current infrastructure score
    - Proposed budget increase (% or $ per capita)
    - Resulting predicted satisfaction score

    The goal: simulate how much gain in satisfaction can be achieved per unit of investment in different counties — helping identify the most efficient allocations.
    """)
