import pandas as pd
import streamlit as st
import math

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

# Streamlit application with step progress bar
st.set_page_config(layout="centered")
st.title("Dynamic Price Evaluation: Guided Workflow")

# Progress bar style and setup
step_labels = ["Upload Files", "Define Parameters", "Rank Views & Layouts", "Calculate & Review"]
current_step = st.session_state.get("current_step", 0)
st.session_state["step_status"] = st.session_state.get("step_status", [False] * len(step_labels))

# Function to render the progress bar
def render_progress_bar():
    progress_bar = "<div style='display: flex; gap: 10px;'>"
    for idx, label in enumerate(step_labels):
        color = "#4CAF50" if idx < current_step else ("blue" if idx == current_step else "gray")
        check_icon = "✔️" if st.session_state["step_status"][idx] else ""
        progress_bar += f"<div style='flex: 1; padding: 10px; background-color: {color}; border-radius: 5px; text-align: center;'>{label} {check_icon}</div>"
    progress_bar += "</div>"
    st.markdown(progress_bar, unsafe_allow_html=True)

render_progress_bar()

# Step 1: Upload Files
if current_step == 0:
    st.markdown("### Step 1: Upload Required Excel Files")
    income_plan_file = st.file_uploader("Upload Income Plan (Excel)", type=["xlsx", "xls"], key="income_plan")
    specification_file = st.file_uploader("Upload Specification (Excel)", type=["xlsx", "xls"], key="specification")

    if income_plan_file and specification_file:
        st.success("Files uploaded successfully.")
        st.session_state["step_status"][0] = True
        if st.button("Next"):
            st.session_state.current_step = 1

# Step 2: Define Parameters
if current_step == 1:
    st.markdown("### Step 2: Define User Parameters")
    base_price = st.number_input("Base Price (per m²)", min_value=0.0, step=0.1)
    spread = st.number_input("Spread for Area Factor", min_value=0.1, step=0.1)
    offset = st.number_input("Offset Value", min_value=0, step=1)
    minimal_area = st.number_input("Minimal Area", min_value=0.1, step=0.1)
    log_base = st.number_input("Logarithmic Base", min_value=1.0, step=0.1)
    step = st.number_input("Step Value for Score Calculation", min_value=0.1, step=0.1)
    incline = st.number_input("Incline for View Factor", min_value=0.1, step=0.1)
    shift = st.number_input("Shift for View Factor", min_value=0, step=1)
    terrace_coefficient = st.number_input("Coefficient for Terrace Factor", min_value=0.0, step=0.1)
    levels_coefficient = st.number_input("Coefficient for Levels Factor", min_value=0.0, step=0.1)
    maxify_adjustment = st.number_input("Adjustment for Maxify Factor", min_value=0.0, step=0.1)

    if st.button("Next"):
        st.session_state["step_status"][1] = True
        st.session_state.current_step = 2

# Step 3: Rank Views & Layouts
if current_step == 2:
    st.markdown("### Step 3: Rank Views and Layouts")
    try:
        specification_data = pd.read_excel(specification_file, engine='openpyxl')
        if 'View from window' not in specification_data.columns:
            specification_data['View from window'] = 'Default View'
        if 'Layout type' not in specification_data.columns:
            specification_data['Layout type'] = 'Default Layout'

        unique_views = specification_data['View from window'].unique()
        unique_layouts = specification_data['Layout type'].unique()

        view_ranking = {view: st.slider(f"Rank for View: {view}", min_value=1, max_value=10, step=1) for view in unique_views}
        layout_ranking = {layout: st.slider(f"Rank for Layout: {layout}", min_value=1, max_value=10, step=1) for layout in unique_layouts}

        if st.button("Next"):
            st.session_state["step_status"][2] = True
            st.session_state.current_step = 3
    except Exception as e:
        st.error(f"Error processing specification file: {e}")

# Step 4: Calculate & Review
if current_step == 3:
    st.markdown("### Step 4: Calculate and Review")
    if st.button("Calculate"):
        try:
            # Perform calculations
            specification_data['Oversold'] = specification_data.apply(
                lambda row: calculate_oversold(row.get('Properties Sold', 0), row.get('Total Properties', 1)), axis=1
            )

            specification_data['Dynamic Price (per m²)'] = base_price
            specification_data['Total Price'] = specification_data['Dynamic Price (per m²)'] * specification_data['Estimated area, m2']
            specification_data['Discount'] = specification_data['Total Price'] * 0.1

            st.session_state["step_status"][3] = True
            st.success("Calculation completed.")
            st.write("### Calculation Results")
            st.dataframe(specification_data)

            st.markdown("### Download Results")
            st.download_button(
                label="Download Updated Data",
                data=specification_data.to_csv(index=False),
                file_name="updated_specification_data.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"An error occurred during calculations: {e}")
