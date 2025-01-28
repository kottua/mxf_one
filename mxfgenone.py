import streamlit as st
import pandas as pdimport streamlit as st
import pandas as pd
import math

# Helper functions translated from PHP

def get_floor_factor_linear(current_floor, max_floor, spread, offset):
    return ((current_floor / max_floor) * spread + offset) / (1 * spread + offset)

def get_floor_factor_logarithmic(current_floor, max_floor, offset, log_base):
    return (math.log(current_floor, log_base) + offset) / (math.log(max_floor, log_base) + offset)

def get_score(base, oversold, step):
    return base + (base * ((oversold + 0.01) ** (1 / step)))

def calculate_dynamic_price(data, base_price, oversold_col, step):
    # Ensure 'Estimated area, m2' is present
    if 'Estimated area, m2' not in data.columns:
        raise KeyError("The column 'Estimated area, m2' is missing in the specification file.")

    data['Score'] = data.apply(lambda row: get_score(base_price, row[oversold_col], step), axis=1)
    data['Dynamic Price'] = data['Score'] * data['Estimated area, m2']
    return data

# Expected columns for validation
EXPECTED_INCOME_PLAN_COLUMNS = ['Property type', 'Year', 'Month', 'Area', 'Sales amount']
EXPECTED_SPECIFICATION_COLUMNS = [
    'Property type', 'Premises ID ', 'Number of unit', 'Number', 'Entrance', 'Floor',
    'Layout type', 'Full price', 'Total area, m2', 'Estimated area, m2',
    'Price per meter', 'Number of rooms', 'Living area, m2', 'Kitchen area, m2',
    'View from window', 'Number of levels', 'Number of loggias', 'Number of balconies',
    'Number of bathrooms with toilets', 'Number of separate bathrooms',
    'Number of terraces', 'Studio', 'Status', 'Sales amount'
]

# Streamlit application
st.title("Dynamic Price Evaluation: Guided Workflow")

st.markdown("### Step 1: Upload Required Excel Files")
# Upload income plan file
income_plan_file = st.file_uploader("Upload Income Plan (Excel)", type=["xlsx", "xls"], key="income_plan")

# Upload specification file
specification_file = st.file_uploader("Upload Specification (Excel)", type=["xlsx", "xls"], key="specification")

# Validate income plan file
if income_plan_file is not None:
    try:
        income_plan_data = pd.read_excel(income_plan_file, engine='openpyxl')
        if list(income_plan_data.columns) == EXPECTED_INCOME_PLAN_COLUMNS:
            st.success("Income Plan file structure is valid.")
            st.write("### Uploaded Income Plan Data")
            st.dataframe(income_plan_data)
        else:
            st.error(f"Invalid Income Plan file structure. Expected columns: {EXPECTED_INCOME_PLAN_COLUMNS}")
    except Exception as e:
        st.error(f"Error reading Income Plan file: {e}")
else:
    st.warning("Please upload the Income Plan file.")

# Validate specification file
if specification_file is not None:
    try:
        specification_data = pd.read_excel(specification_file, engine='openpyxl')
        if list(specification_data.columns) == EXPECTED_SPECIFICATION_COLUMNS:
            st.success("Specification file structure is valid.")
            st.write("### Uploaded Specification Data")
            st.dataframe(specification_data)
        else:
            st.error(f"Invalid Specification file structure. Expected columns: {EXPECTED_SPECIFICATION_COLUMNS}")
    except Exception as e:
        st.error(f"Error reading Specification file: {e}")
else:
    st.warning("Please upload the Specification file.")

if income_plan_file is not None and specification_file is not None:
    st.markdown("### Step 2: Define Calculation Parameters")
    base_price = st.number_input("Base Price", min_value=0.0, step=0.1)
    oversold_col = st.selectbox("Select the Oversold Column from Specification", specification_data.columns)
    step = st.number_input("Step Value", min_value=0.1, step=0.1)

    if st.button("Calculate Dynamic Prices"):
        try:
            updated_data = calculate_dynamic_price(specification_data, base_price, oversold_col, step)
            st.success("Dynamic Prices Calculated Successfully")
            st.write("### Updated Specification Data with Dynamic Prices")
            st.dataframe(updated_data)

            st.markdown("### Step 3: Download Updated Data")
            st.download_button(
                label="Download Updated Specification Data",
                data=updated_data.to_csv(index=False),
                file_name="updated_specification_data.csv",
                mime="text/csv"
            )
        except KeyError as e:
            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

import math

# Helper functions translated from PHP

def get_floor_factor_linear(current_floor, max_floor, spread, offset):
    return ((current_floor / max_floor) * spread + offset) / (1 * spread + offset)

def get_floor_factor_logarithmic(current_floor, max_floor, offset, log_base):
    return (math.log(current_floor, log_base) + offset) / (math.log(max_floor, log_base) + offset)

def get_score(base, oversold, step):
    return base + (base * ((oversold + 0.01) ** (1 / step)))

def calculate_dynamic_price(data, base_price, oversold_col, step):
    data['Score'] = data.apply(lambda row: get_score(base_price, row[oversold_col], step), axis=1)
    data['Dynamic Price'] = data['Score'] * data['Estimated Area']
    return data

# Expected columns for validation
EXPECTED_INCOME_PLAN_COLUMNS = ['Property type', 'Year', 'Month', 'Area', 'Sales amount']
EXPECTED_SPECIFICATION_COLUMNS = [
    'Property type', 'Premises ID ', 'Number of unit', 'Number', 'Entrance', 'Floor',
    'Layout type', 'Full price', 'Total area, m2', 'Estimated area, m2',
    'Price per meter', 'Number of rooms', 'Living area, m2', 'Kitchen area, m2',
    'View from window', 'Number of levels', 'Number of loggias', 'Number of balconies',
    'Number of bathrooms with toilets', 'Number of separate bathrooms',
    'Number of terraces', 'Studio', 'Status', 'Sales amount'
]

# Streamlit application
st.title("Dynamic Price Evaluation: Guided Workflow")

st.markdown("### Step 1: Upload Required Excel Files")
# Upload income plan file
income_plan_file = st.file_uploader("Upload Income Plan (Excel)", type=["xlsx", "xls"], key="income_plan")

# Upload specification file
specification_file = st.file_uploader("Upload Specification (Excel)", type=["xlsx", "xls"], key="specification")

# Validate income plan file
if income_plan_file is not None:
    income_plan_data = pd.read_excel(income_plan_file)
    if list(income_plan_data.columns) == EXPECTED_INCOME_PLAN_COLUMNS:
        st.success("Income Plan file structure is valid.")
        st.write("### Uploaded Income Plan Data")
        st.dataframe(income_plan_data)
    else:
        st.error(f"Invalid Income Plan file structure. Expected columns: {EXPECTED_INCOME_PLAN_COLUMNS}")
else:
    st.warning("Please upload the Income Plan file.")

# Validate specification file
if specification_file is not None:
    specification_data = pd.read_excel(specification_file)
    if list(specification_data.columns) == EXPECTED_SPECIFICATION_COLUMNS:
        st.success("Specification file structure is valid.")
        st.write("### Uploaded Specification Data")
        st.dataframe(specification_data)
    else:
        st.error(f"Invalid Specification file structure. Expected columns: {EXPECTED_SPECIFICATION_COLUMNS}")
else:
    st.warning("Please upload the Specification file.")

if income_plan_file is not None and specification_file is not None:
    st.markdown("### Step 2: Define Calculation Parameters")
    base_price = st.number_input("Base Price", min_value=0.0, step=0.1)
    oversold_col = st.selectbox("Select the Oversold Column from Specification", specification_data.columns)
    step = st.number_input("Step Value", min_value=0.1, step=0.1)

    if st.button("Calculate Dynamic Prices"):
        updated_data = calculate_dynamic_price(specification_data, base_price, oversold_col, step)
        st.success("Dynamic Prices Calculated Successfully")
        st.write("### Updated Specification Data with Dynamic Prices")
        st.dataframe(updated_data)

        st.markdown("### Step 3: Download Updated Data")
        st.download_button(
            label="Download Updated Specification Data",
            data=updated_data.to_csv(index=False),
            file_name="updated_specification_data.csv",
            mime="text/csv"
        )
