import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset with caching
@st.cache_data
def load_data():
    df = pd.read_csv("data/Eldercare_Tiers_2022_FullCountyCoverage.csv")
    df["FIPS"] = df["FIPS"].astype(str).str.zfill(5)

    # Simulate satisfaction score (inversely proportional to vulnerability)
    df["CurrentSatisfaction"] = df["ElderVulnerabilityIndex"].apply(
        lambda x: round(max(0.1, min(1.0, 1 - x)), 3) if pd.notna(x) else None
    )

    # Replace with actual state names if available
    df["StateName"] = df["State"]  # Can map FIPS to full names later
    return df

df = load_data()

# GeoJSON URL for U.S. counties
geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

# App config
st.set_page_config(page_title="S.A.G.E. – Eldercare Simulation Tool", layout="wide")

# Page selector
pages = ["🏠 Welcome", "📊 Vulnerability Index Map", "📈 Satisfaction Simulation"]
page = st.sidebar.radio("Navigate", pages)

# -------------------- Welcome Page --------------------
if page == "🏠 Welcome":
    st.title("S.A.G.E. – Sustainable Aging Governance Engine")
    st.subheader("Equity-focused Decision Support for Eldercare")

    st.markdown("""
    S.A.G.E. helps local governments, nonprofits, and policymakers understand where eldercare resources are most needed,
    and how investments could improve community satisfaction. It combines:
    
    - **CDC Social Vulnerability Index (SVI)**
    - **U.S. Census data**
    - A synthetic satisfaction projection model

    The tool offers both a **vulnerability map** and a **satisfaction impact simulation** to guide resource allocation decisions.
    """)

    st.image("data/vulnerability_demo_image.png", use_column_width=True,
             caption="Regional Disparities in Eldercare Vulnerability (demo layout)")

    st.info("Use the sidebar to explore by map type or simulation scenario.")

# -------------------- Vulnerability Map --------------------
elif page == "📊 Vulnerability Index Map":
    st.title("📊 Eldercare Vulnerability Index (by County)")

    # Filters
    selected_states = st.sidebar.multiselect("Filter by State", sorted(df["StateName"].unique()))
    selected_tiers = st.sidebar.multiselect(
        "Filter by Tier",
        options=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low", "No Data"],
        default=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low"]
    )

    filtered_df = df.copy()
    if selected_states:
        filtered_df = filtered_df[filtered_df["StateName"].isin(selected_states)]
    if selected_tiers:
        filtered_df = filtered_df[filtered_df["Tier"].isin(selected_tiers)]

    # Map
    st.markdown(f"**Displaying {len(filtered_df)} counties.**")
    fig = px.choropleth(
        filtered_df,
        geojson=geojson_url,
        locations="FIPS",
        color="ElderVulnerabilityIndex",
        color_continuous_scale="OrRd",
        range_color=(0, 1),
        scope="usa",
        hover_data=["County", "State", "Tier", "ElderVulnerabilityIndex"]
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Data source: CDC SVI 2022 + U.S. Census (processed by S.A.G.E.)")

# -------------------- Satisfaction Simulation --------------------
elif page == "📈 Satisfaction Simulation":
    st.title("📈 Satisfaction Simulation – Investment Impact by County")

    selected_states = st.sidebar.multiselect("Filter by State", sorted(df["StateName"].unique()))
    selected_tiers = st.sidebar.multiselect(
        "Filter by Tier",
        options=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low", "No Data"],
        default=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low"]
    )

    investment_factor = st.sidebar.slider(
        "Investment Effectiveness",
        min_value=0.0, max_value=1.0, value=0.2, step=0.05,
        help="Higher values simulate stronger satisfaction improvements for vulnerable counties."
    )

    sim_df = df.copy()
    if selected_states:
        sim_df = sim_df[sim_df["StateName"].isin(selected_states)]
    if selected_tiers:
        sim_df = sim_df[sim_df["Tier"].isin(selected_tiers)]

    sim_df["PredictedSatisfaction"] = sim_df.apply(
        lambda row: round(min(1.0, row["CurrentSatisfaction"] + row["ElderVulnerabilityIndex"] * investment_factor), 3)
        if pd.notna(row["CurrentSatisfaction"]) else None,
        axis=1
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟠 Current Satisfaction")
        fig_before = px.choropleth(
            sim_df,
            geojson=geojson_url,
            locations="FIPS",
            color="CurrentSatisfaction",
            color_continuous_scale="Greens",
            range_color=(0, 1),
            scope="usa",
            hover_data=["County", "State", "Tier", "CurrentSatisfaction"]
        )
        fig_before.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_before, use_container_width=True)

    with col2:
        st.subheader("🟢 Projected Satisfaction (After Investment)")
        fig_after = px.choropleth(
            sim_df,
            geojson=geojson_url,
            locations="FIPS",
            color="PredictedSatisfaction",
            color_continuous_scale="Greens",
            range_color=(0, 1),
            scope="usa",
            hover_data=["County", "State", "Tier", "PredictedSatisfaction"]
        )
        fig_after.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_after, use_container_width=True)

    st.caption("Projection model for demonstration only. Scores simulate directional improvement.")


