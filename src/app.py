

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
    """)
