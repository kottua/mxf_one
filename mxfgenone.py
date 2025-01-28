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

# Streamlit application
st.title("Dynamic Price Evaluation: Guided Workflow")

st.markdown("### Step 1: Upload Required Excel Files")
# Upload income plan file
income_plan_file = st.file_uploader("Upload Income Plan (Excel)", type=["xlsx", "xls"], key="income_plan")

# Upload specification file
specification_file = st.file_uploader("Upload Specification (Excel)", type=["xlsx", "xls"], key="specification")

# Additional user-defined parameters
st.markdown("### Step 2: Define User Parameters")
base_price = st.number_input("Base Price", min_value=0.0, step=0.1)
spread = st.number_input("Spread for Area Factor", min_value=0.1, step=0.1)
offset = st.number_input("Offset Value", min_value=0, step=1)
minimal_area = st.number_input("Minimal Area", min_value=0.1, step=0.1)
log_base = st.number_input("Logarithmic Base", min_value=1.0, step=0.1)
step = st.number_input("Step Value for Score Calculation", min_value=0.1, step=0.1)
incline = st.number_input("Incline for View Factor", min_value=0.1, step=0.1)
shift = st.number_input("Shift for View Factor", min_value=0, step=1)
terrace_coefficient = st.number_input("Coefficient for Terrace Factor", min_value=0.0, step=0.1)
levels_coefficient = st.number_input("Coefficient for Levels Factor", min_value=0.0, step=0.1)

# Validate uploaded files
if income_plan_file is not None:
    try:
        income_plan_data = pd.read_excel(income_plan_file, engine='openpyxl')
        st.success("Income Plan file loaded successfully.")
        st.write("### Income Plan Data Preview")
        st.dataframe(income_plan_data)
    except Exception as e:
        st.error(f"Error reading Income Plan file: {e}")

if specification_file is not None:
    try:
        specification_data = pd.read_excel(specification_file, engine='openpyxl')
        st.success("Specification file loaded successfully.")
        st.write("### Specification Data Preview")
        st.dataframe(specification_data)
    except Exception as e:
        st.error(f"Error reading Specification file: {e}")

# Perform calculations
if specification_file is not None:
    if st.button("Calculate Dynamic Prices"):
        try:
            specification_data['Area Factor'] = specification_data.apply(
                lambda row: get_area_factor_linear(spread, row['Estimated area, m2'], offset, minimal_area), axis=1
            )
            specification_data['View Factor'] = specification_data.apply(
                lambda row: get_view_factor_value(row.get('View', 0), 10, incline, shift), axis=1
            )
            specification_data['Layout Factor'] = specification_data.apply(
                lambda row: get_layout_factor_value(row.get('Layout', 0), 10, incline, shift), axis=1
            )
            specification_data['Terrace Factor'] = specification_data.apply(
                lambda row: get_terrace_factor_value(row.get('Has Terrace', False), terrace_coefficient), axis=1
            )
            specification_data['Levels Factor'] = specification_data.apply(
                lambda row: get_levels_factor_value(row.get('Levels', 1), levels_coefficient), axis=1
            )
            specification_data['Score'] = specification_data.apply(
                lambda row: get_score(base_price, row.get('Oversold', 0), step), axis=1
            )
            specification_data['Dynamic Price'] = specification_data['Score'] * specification_data['Estimated area, m2']
            specification_data['Discount'] = specification_data['Dynamic Price'] * 0.1

            st.success("Dynamic Prices Calculated Successfully.")
            st.write("### Updated Specification Data with Calculations")
            st.dataframe(specification_data[['Premises ID ', 'Dynamic Price', 'Discount']])

            st.markdown("### Step 3: Download Results")
            st.download_button(
                label="Download Updated Data",
                data=specification_data.to_csv(index=False),
                file_name="updated_specification_data.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"An error occurred during calculations: {e}")
