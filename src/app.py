import streamlit as st
import pandas as pd
import plotly.express as px

# Load full dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data/Eldercare_Tiers_2022_FullCountyCoverage.csv")
    df["FIPS"] = df["FIPS"].astype(str).str.zfill(5)

    # Simulated current satisfaction (inverse of vulnerability)
    df["CurrentSatisfaction"] = df["ElderVulnerabilityIndex"].apply(
        lambda x: round(max(0.1, min(1.0, 1 - x)), 3) if pd.notna(x) else None
    )

    return df

df = load_data()

# Sidebar filters
st.sidebar.title("S.A.G.E. Filters")
selected_states = st.sidebar.multiselect(
    "Filter by State",
    sorted(df["State"].unique())
)

selected_tiers = st.sidebar.multiselect(
    "Filter by Tier",
    options=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low", "No Data"],
    default=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low"]
)

investment_factor = st.sidebar.slider(
    "Investment Effectiveness (%)",
    min_value=0.0, max_value=1.0, value=0.2, step=0.05,
    help="This controls how much satisfaction increases for higher vulnerability areas."
)

# Apply filters
filtered = df.copy()
if selected_states:
    filtered = filtered[filtered["State"].isin(selected_states)]
if selected_tiers:
    filtered = filtered[filtered["Tier"].isin(selected_tiers)]

# Calculate projected satisfaction
filtered["PredictedSatisfaction"] = filtered.apply(
    lambda row: round(min(1.0, row["CurrentSatisfaction"] + row["ElderVulnerabilityIndex"] * investment_factor), 3)
    if pd.notna(row["CurrentSatisfaction"]) else None,
    axis=1
)

# GeoJSON source
geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

# App layout
st.title("S.A.G.E. – Sustainable Aging Governance Engine")
st.markdown("Simulating satisfaction improvement from targeted eldercare investment, driven by equity and need.")

st.markdown(f"**Currently displaying {len(filtered)} counties**.")

# Layout two maps side-by-side
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟠 Current Satisfaction (Before Investment)")
    fig1 = px.choropleth(
        filtered,
        geojson=geojson_url,
        locations="FIPS",
        color="CurrentSatisfaction",
        color_continuous_scale="Greens",
        range_color=(0, 1),
        scope="usa",
        hover_data=["County", "State", "Tier", "ElderVulnerabilityIndex", "CurrentSatisfaction"]
    )
    fig1.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🟢 Projected Satisfaction (After Investment)")
    fig2 = px.choropleth(
        filtered,
        geojson=geojson_url,
        locations="FIPS",
        color="PredictedSatisfaction",
        color_continuous_scale="Greens",
        range_color=(0, 1),
        scope="usa",
        hover_data=["County", "State", "Tier", "ElderVulnerabilityIndex", "PredictedSatisfaction"]
    )
    fig2.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    st.plotly_chart(fig2, use_container_width=True)

st.caption("Data: CDC SVI 2022 • Simulated by S.A.G.E. modeling logic")

