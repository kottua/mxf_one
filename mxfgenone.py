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

def calculate_dynamic_price(data, base_price, oversold_col, step):
    # Ensure 'Estimated area, m2' is present
    if 'Estimated area, m2' not in data.columns:
        raise KeyError("The column 'Estimated area, m2' is missing in the specification file.")

    # Ensure critical columns are numeric
    try:
        data['Estimated area, m2'] = pd.to_numeric(data['Estimated area, m2'], errors='coerce')
        if oversold_col not in data.columns:
            data[oversold_col] = 0  # Add a virtual column with default value if missing
            st.warning(f"Column '{oversold_col}' is missing. Defaulting to 0 for all rows.")
        data[oversold_col] = pd.to_numeric(data[oversold_col], errors='coerce').fillna(0)  # Fill NaN with 0
    except Exception as e:
        raise ValueError(f"Error converting columns to numeric: {e}")

    # Debugging: Check the unique values in critical columns
    st.write("### Unique values in 'Estimated area, m2':")
    st.write(data['Estimated area, m2'].unique())
    st.write("### Unique values in the selected oversold column:")
    st.write(data[oversold_col].unique())

    # Debugging: Check data before dropping NaN
    st.write("### Data before dropping NaN:")
    st.dataframe(data[['Premises ID ', 'Estimated area, m2', oversold_col]].head())

    # Drop rows with NaN values in critical columns
    data = data.dropna(subset=['Estimated area, m2'])

    # Debugging: Check data after dropping NaN
    if data.empty:
        st.warning("No valid rows remain after dropping rows with NaN values.")
        st.write("### Data after dropping NaN:")
        st.dataframe(data)
        raise ValueError("No valid rows available after dropping NaN values in critical columns.")

    st.write("### Data after dropping NaN:")
    st.dataframe(data[['Premises ID ', 'Estimated area, m2', oversold_col]].head())

    data['Score'] = data.apply(lambda row: get_score(base_price, row[oversold_col], step), axis=1)
    data['Dynamic Price'] = data['Score'] * data['Estimated area, m2']

    # Calculate Discount (example logic: 10% of Dynamic Price)
    data['Discount'] = data['Dynamic Price'] * 0.1

    # Ensure key columns are populated
    if data[['Premises ID ', 'Dynamic Price', 'Discount']].isnull().any().any():
        raise ValueError("Some key columns (Premises ID, Dynamic Price, or Discount) have missing values.")

    # Keep only relevant columns
    result = data[['Premises ID ', 'Dynamic Price', 'Discount']]
    return result

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
        except ValueError as e:
            st.error(f"Data validation error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
