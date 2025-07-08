import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="S.A.G.E. – Eldercare Simulation Tool", layout="wide")

# Load main dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data/Eldercare_Tiers_2022_FullCountyCoverage.csv")
    df["FIPS"] = df["FIPS"].astype(str).str.zfill(5)
    df["CurrentSatisfaction"] = df["ElderVulnerabilityIndex"].apply(
        lambda x: round(max(0.1, min(1.0, 1 - x)), 3) if pd.notna(x) else None
    )
    state_fips_to_abbr = {
        "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
        "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
        "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
        "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
        "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
        "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
        "54": "WV", "55": "WI", "56": "WY"
    }
    df["StateFIPS"] = df["FIPS"].str[:2]
    df["StateAbbr"] = df["StateFIPS"].map(state_fips_to_abbr)
    return df

# Load disparity dataset
@st.cache_data
def load_disparity_data():
    df = pd.read_csv("data/Unified_SAGE_DisparityDataset.csv", dtype={"FIPS": str})
    df["FIPS"] = df["FIPS"].str.zfill(5)
    return df

df = load_data()
disparity_df = load_disparity_data()
geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

# Page Navigation
pages = [
    "🏠 Welcome",
    "🩺 Healthcare Disparity Map",
    "📊 Vulnerability Index Map",
    "📈 Satisfaction Simulation"
]
page = st.sidebar.radio("Navigate", pages)

# -------------------- Welcome --------------------
if page == "🏠 Welcome":
    st.title("S.A.G.E. – Sustainable Aging Governance Engine")
    st.subheader("Equity-focused Decision Support for Eldercare")
    st.markdown("""
    S.A.G.E. is an equity-first decision support tool that helps identify and simulate how public health investments
    can improve eldercare across the United States. It combines:

    - **CDC Social Vulnerability Index (SVI)**
    - **U.S. Census demographic and aging data**
    - **Medicare & Medicaid chronic care disparity data**
    - A **synthetic satisfaction projection model**

    The platform supports local governments, nonprofits, and policy teams to **prioritize regions** with the greatest need
    using unified and dynamic data.
    """)
    st.info("Use the sidebar to explore map types and investment simulations.")

# -------------------- Healthcare Disparity Map --------------------
elif page == "🩺 Healthcare Disparity Map":
    st.title("🩺 Healthcare Disparity Map – Medicare/Medicaid Resource Gaps")
    st.markdown("""
    This map visualizes key eldercare and insurance-related disparities across counties using:

    - **Medicare/Medicaid average chronic costs**
    - **Eldercare population rate (U.S. Census)**
    - **Uninsured rates or insurance coverage (proxy)**

    Use the filters and layer selector to examine support gaps from multiple dimensions.
    """)

    selected_states = st.sidebar.multiselect("Filter by State", sorted(disparity_df["ST_ABBR"].dropna().unique()))
    layer_option = st.sidebar.radio("Select Data Layer", [
        "AvgChronicCost (Medicare/Medicaid)",
        "EldercareRate (Census)",
        "UninsuredRate (Coverage)"
    ])

    disp_filtered = disparity_df.copy()
    if selected_states:
        disp_filtered = disp_filtered[disp_filtered["ST_ABBR"].isin(selected_states)]

    # Safely map the selected layer option to column
    layer_mapping = {
        "AvgChronicCost (Medicare/Medicaid)": "AvgChronicCost",
        "EldercareRate (Census)": "EldercareRate",
        "UninsuredRate (Coverage)": "UninsuredRate"
    }
    layer_column = layer_mapping.get(layer_option)

    if layer_column in disp_filtered.columns:
        fig = px.choropleth(
            disp_filtered,
            geojson=geojson_url,
            locations="FIPS",
            color=layer_column,
            color_continuous_scale="Reds" if "Cost" in layer_column else "Blues",
            scope="usa",
            range_color=(disp_filtered[layer_column].min(), disp_filtered[layer_column].max()),
            hover_data=["COUNTY", "STATE", layer_column]
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Data column '{layer_column}' not found in dataset. Please check column names.")

    st.caption("Data: CMS, U.S. Census, CDC SVI")

# -------------------- Vulnerability Index --------------------
elif page == "📊 Vulnerability Index Map":
    st.title("📊 Eldercare Vulnerability Index (by County)")
    selected_states = st.sidebar.multiselect("Filter by State", sorted(df["StateAbbr"].dropna().unique()))
    selected_tiers = st.sidebar.multiselect(
        "Filter by Tier",
        options=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low", "No Data"],
        default=["Tier 1: Critical", "Tier 2: High", "Tier 3: Moderate", "Tier 4: Low"]
    )
    filtered_df = df.copy()
    if selected_states:
        filtered_df = filtered_df[filtered_df["StateAbbr"].isin(selected_states)]
    if selected_tiers:
        filtered_df = filtered_df[filtered_df["Tier"].isin(selected_tiers)]
    st.markdown(f"**Displaying {len(filtered_df)} counties.**")
    fig = px.choropleth(
        filtered_df,
        geojson=geojson_url,
        locations="FIPS",
        color="ElderVulnerabilityIndex",
        color_continuous_scale="OrRd",
        range_color=(0, 1),
        scope="usa",
        hover_data=["County", "StateAbbr", "Tier", "ElderVulnerabilityIndex"]
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Data: CDC SVI 2022 + U.S. Census (processed by S.A.G.E.)")

# -------------------- Satisfaction Simulation --------------------
elif page == "📈 Satisfaction Simulation":
    st.title("📈 Satisfaction Simulation – Investment Impact by County")
    selected_states = st.sidebar.multiselect("Filter by State", sorted(df["StateAbbr"].dropna().unique()))
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
        sim_df = sim_df[sim_df["StateAbbr"].isin(selected_states)]
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
            hover_data=["County", "StateAbbr", "Tier", "CurrentSatisfaction"]
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
            hover_data=["County", "StateAbbr", "Tier", "PredictedSatisfaction"]
        )
        fig_after.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_after, use_container_width=True)
    st.caption("Projection model for demonstration purposes only.")


