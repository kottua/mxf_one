import streamlit as st
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
    data['Score'] = data.apply(lambda row: get_score(base_price, row[oversold_col], step), axis=1)
    data['Dynamic Price'] = data['Score'] * data['Estimated Area']
    return data

# Streamlit application
st.title("Dynamic Price Evaluation: Guided Workflow")

st.markdown("### Step 1: Upload Required Excel Files")
# Upload initial sales data
sales_file = st.file_uploader("Upload Sales Data (Excel)", type=["xlsx", "xls"], key="sales")

# Upload any additional configuration data if required
config_file = st.file_uploader("Upload Configuration Data (Excel)", type=["xlsx", "xls"], key="config")

if sales_file is not None:
    sales_data = pd.read_excel(sales_file)
    st.write("### Uploaded Sales Data")
    st.dataframe(sales_data)
else:
    st.warning("Please upload sales data to proceed.")

if config_file is not None:
    config_data = pd.read_excel(config_file)
    st.write("### Uploaded Configuration Data")
    st.dataframe(config_data)
else:
    st.info("Upload configuration data if applicable.")

if sales_file is not None:
    st.markdown("### Step 2: Define Calculation Parameters")
    base_price = st.number_input("Base Price", min_value=0.0, step=0.1)
    oversold_col = st.selectbox("Select the Oversold Column", sales_data.columns)
    step = st.number_input("Step Value", min_value=0.1, step=0.1)

    if st.button("Calculate Dynamic Prices"):
        updated_data = calculate_dynamic_price(sales_data, base_price, oversold_col, step)
        st.success("Dynamic Prices Calculated Successfully")
        st.write("### Updated Sales Data")
        st.dataframe(updated_data)

        st.markdown("### Step 3: Download Updated Data")
        st.download_button(
            label="Download Updated Sales Data",
            data=updated_data.to_csv(index=False),
            file_name="updated_sales_data.csv",
            mime="text/csv"
        )

    st.markdown("### Step 4: Additional Calculations (Optional)")
    current_floor = st.number_input("Current Floor", min_value=1, step=1)
    max_floor = st.number_input("Max Floor", min_value=1, step=1)
    spread = st.number_input("Spread", min_value=0.0, step=0.1)
    offset = st.number_input("Offset", min_value=0, step=1)

    if st.button("Calculate Linear Floor Factor"):
        linear_factor = get_floor_factor_linear(current_floor, max_floor, spread, offset)
        st.success(f"Linear Floor Factor: {linear_factor}")

    log_base = st.number_input("Log Base", min_value=1.0, step=0.1)
    if st.button("Calculate Logarithmic Floor Factor"):
        log_factor = get_floor_factor_logarithmic(current_floor, max_floor, offset, log_base)
        st.success(f"Logarithmic Floor Factor: {log_factor}")
