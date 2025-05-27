import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/Eldercare_Regional_Dataset.csv")
    df["SVI_rank"] = df["SVI"].rank(ascending=False)
df["Age65_rank"] = df["PopulationOver65"].rank(ascending=False)
df["CompositePriorityScore"] = (df["SVI_rank"] + df["Age65_rank"]) / 2
df["ElderVulnerabilityIndex"] = df["SVI"] * (df["PopulationOver65"] / 100)
    return df

df = load_data()

# User persona selector
user_role = st.sidebar.selectbox("I am a...", ["General User", "County Planner", "State Policy Analyst", "Community Advocate"])

# Page navigation
page = st.sidebar.radio("Navigate", ["Welcome", "National Summary", "County Explorer", "Simulation Tool (Coming Soon)", "Feedback"])

# Welcome Page
if page == "Welcome":
    st.title("S.A.G.E. – Sustainable Aging Governance Engine")
    st.subheader("AI-powered tool for equitable eldercare resource allocation")
    st.markdown(f"**Role selected:** {user_role}")
    st.markdown("""
    Welcome to S.A.G.E., a decision intelligence tool that helps local governments identify and prioritize regions
    for eldercare investment. This platform integrates social vulnerability data, aging demographics, and predictive
    modeling to help allocate resources where they will have the greatest impact.

    **Key Decision-Making Factors:**
    - **SVI (Social Vulnerability Index):** How structurally disadvantaged is the region? *(Higher is worse)*
    - **Population Over 65 (%):** What proportion of the population is elderly? *(Higher signals greater need)*
    - **Infrastructure Score:** How well-prepared is the region to support eldercare? *(Higher is better)*
    - **Projected Satisfaction Impact:** What return could we expect on additional investment? *(Higher is better)*

    Use the sidebar to explore real data and simulate decisions.

**About the Roles:**
- **County Planners** need localized, budget-justified recommendations.
- **State Policy Analysts** want cross-county comparisons and infrastructure trends.
- **Community Advocates** focus on equity gaps and local vulnerability hotspots.
- **General Users** can explore national data with contextual support.

The app tailors narrative output and indicators based on these personas to make the tool accessible and action-oriented.
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

    if user_role == "County Planner":
        st.markdown("#### Narrative Summary")
        st.markdown(f"{selected_county} County faces moderate eldercare vulnerability with a {selected_row['SVI']:.2f} SVI and {selected_row['InfrastructureScore']:.2f} infrastructure readiness. Recommended priority: **{recommend(selected_row)}**")

    st.markdown("### Top 10 Counties by Elder Vulnerability Index (Higher = More Vulnerable)")
    top_10 = filtered_df.sort_values("ElderVulnerabilityIndex", ascending=False).head(10)
    st.dataframe(top_10[["County", "SVI", "PopulationOver65", "ElderVulnerabilityIndex"]].reset_index(drop=True))

# National Summary Page
elif page == "National Summary":
    st.title("National Summary of Eldercare Vulnerability")

    st.markdown("#### Top 10 Most Vulnerable Counties Nationwide (Higher = More Urgent Need)")
    top_counties = df.sort_values("ElderVulnerabilityIndex", ascending=False).head(10)
    st.dataframe(top_counties[["County", "State", "SVI", "PopulationOver65", "ElderVulnerabilityIndex"]].reset_index(drop=True))

    st.markdown("#### Top 10 High-Priority Counties (Based on Composite Ranking of SVI and Age 65%)")
top_priority = df.sort_values("CompositePriorityScore").head(10)
styled_df = top_priority[["County", "State", "SVI", "PopulationOver65", "InfrastructureScore", "CompositePriorityScore"]] \
    .reset_index(drop=True) \
    .style.apply(lambda x: ['background-color: #ffcccc' if x.name < 3 else '' for _ in x], axis=1)
st.dataframe(styled_df)

    st.markdown("#### Top 10 States by Average Elder Vulnerability Index (Higher = More Vulnerable)")
    state_avg = df.groupby("State")["ElderVulnerabilityIndex"].mean().sort_values(ascending=False).head(10)
    st.dataframe(state_avg.reset_index().rename(columns={"ElderVulnerabilityIndex": "Avg Elder Vulnerability Index"}))

    st.markdown("#### Visualization: Statewide Average Vulnerability")
    fig, ax = plt.subplots(figsize=(10, 5))
    state_avg.sort_values().plot(kind='barh', ax=ax, color='gray')
    ax.set_xlabel("Average Elder Vulnerability Index")
    ax.set_ylabel("State")
    ax.set_title("Average Elder Vulnerability Index by State")
    st.pyplot(fig)

    st.markdown("#### Insights and Ideas for Further Analysis")
    st.markdown("""
    - Identify geographic clusters of high vulnerability
    - Highlight states with high variability (some counties low, others extremely high)
    - Compare average SVI to average infrastructure score per state
    - Flag counties with high elder population but low infrastructure scores as under-resourced
    - Visualize vulnerability vs satisfaction to identify underperformers and potential improvement targets
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

    **Challenge:** Collecting outcome-linked satisfaction data is limited, and building a proxy model with credible assumptions is our current research focus.
    """)

# Feedback Page
elif page == "Feedback":
    st.title("We Value Your Feedback")
    st.markdown("If you’re a local policymaker, health leader, or community advocate — we’d love your thoughts.")
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        org = st.text_input("Organization")
        role = st.text_input("Your Role")
        feedback = st.text_area("What worked well? What could be improved?")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Thank you! Your feedback has been recorded.")
