import pandas as pd
import streamlit as st
import math
from streamlit_elements import mui, html

# Helper functions translated from PHP

def get_floor_factor_linear(current_floor, max_floor, spread, offset):
    return ((current_floor / max_floor) * spread + offset) / (1 * spread + offset)

def get_floor_factor_logarithmic(current_floor, max_floor, offset, log_base):
    return (math.log(current_floor, log_base) + offset) / (math.log(max_floor, log_base) + offset)

def get_score(base, oversold, step):
    return base + (base * ((oversold + 0.01) ** (1 / step)))

def get_area_factor_linear(spread, estimated_area, offset, minimal_area):
    return abs(((offset - estimated_area) / spread) / ((offset - minimal_area) / spread))

def get_area_factor_logarithmic(log_base, estimated_area, offset, minimal_area):
    return (math.log(estimated_area, log_base) + offset) / (math.log(minimal_area, log_base) + offset)

def get_area_factor_power(filling, estimated_area, minimal_area):
    return (2 ** (filling * estimated_area)) / (2 ** (filling * minimal_area))

def get_area_factor_value(area_factor, spread):
    return area_factor + ((1 - area_factor) / spread)

def get_view_factor_value(current_view_value, max_view_value, incline, shift):
    return ((current_view_value / max_view_value) * incline) + shift

def get_layout_factor_value(current_layout_value, max_layout_value, incline, shift):
    return ((current_layout_value / max_layout_value) * incline) + shift

def get_terrace_factor_value(property_has_terrace, coefficient):
    return coefficient if property_has_terrace else 0

def get_levels_factor_value(levels_qty, coefficient):
    return levels_qty * coefficient

def get_maxify_factor_value(base_factor, max_factor, adjustment):
    return base_factor + (max_factor * adjustment)

def calculate_oversold(properties_sold, total_properties):
    if total_properties == 0:
        return 0
    return properties_sold / total_properties

# Streamlit application
st.title("Dynamic Price Evaluation: Guided Workflow")

# Step management
steps = ["Upload Files", "Define Parameters", "Rank Views & Layouts", "Calculate Results"]
current_step = st.session_state.get("current_step", 0)

def set_step(step):
    st.session_state.current_step = step
    st.experimental_rerun()

# Progress bar with steps
def render_progress_bar():
    for i, step in enumerate(steps):
        color = "green" if i < current_step else ("blue" if i == current_step else "gray")
        mui.Button(
            step,
            variant="contained",
            color=color,
            disabled=(i > current_step),
            onClick=lambda i=i: set_step(i),
        ).style(margin="0 5px")

with st.sidebar:
    st.markdown("### Progress")
    render_progress_bar()

# Steps logic
if current_step == 0:
    st.markdown("### Step 1: Upload Required Excel Files")
    income_plan_file = st.file_uploader("Upload Income Plan (Excel)", type=["xlsx", "xls"], key="income_plan")
    specification_file = st.file_uploader("Upload Specification (Excel)", type=["xlsx", "xls"], key="specification")

    if income_plan_file and specification_file:
        st.success("Files uploaded successfully. Click Next to proceed.")
        if st.button("Next"):
            set_step(1)

elif current_step == 1:
    st.markdown("### Step 2: Define User Parameters")
    base_price = st.number_input("Base Price (per m²)", min_value=0.0, step=0.1)
    spread = st.number_input("Spread for Area Factor", min_value=0.1, step=0.1)
    offset = st.number_input("Offset Value", min_value=0, step=1)
    minimal_area = st.number_input("Minimal Area", min_value=0.1, step=0.1)
    log_base = st.number_input("Logarithmic Base", min_value=1.0, step=0.1)
    step = st.number_input("Step Value for Score Calculation", min_value=0.1, step=0.1)

    if st.button("Next"):
        set_step(2)

elif current_step == 2:
    st.markdown("### Step 3: Rank Views and Layouts")

    specification_data = pd.read_excel(specification_file, engine='openpyxl')

    if 'View from window' not in specification_data.columns:
        specification_data['View from window'] = 'Default View'
        st.warning("Column 'View from window' is missing. A default value has been assigned.")

    if 'Layout type' not in specification_data.columns:
        specification_data['Layout type'] = 'Default Layout'
        st.warning("Column 'Layout type' is missing. A default value has been assigned.")

    unique_views = specification_data['View from window'].unique()
    unique_layouts = specification_data['Layout type'].unique()

    view_ranking = {}
    layout_ranking = {}

    st.write("Assign a rank from 1 to 10 for each unique view and layout.")
    for view in unique_views:
        view_ranking[view] = st.slider(f"Rank for View: {view}", min_value=1, max_value=10, step=1)

    for layout in unique_layouts:
        layout_ranking[layout] = st.slider(f"Rank for Layout: {layout}", min_value=1, max_value=10, step=1)

    if st.button("Next"):
        set_step(3)

elif current_step == 3:
    st.markdown("### Step 4: Calculate Results")
    if st.button("Calculate"):
        # Here you can implement calculations
        st.success("Calculations completed successfully!")

    if st.button("Restart"):
        set_step(0)
