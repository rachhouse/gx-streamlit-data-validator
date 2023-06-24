"""Entrypoint Streamlit app file to run the proof-of-concept data validator with
static expectations."""

import great_expectations as gx
import streamlit as st

import gx_streamlit_data_validator.utils as utils

# Define expectations to be run and displayed in app output.
# For more expectations and expectation details, visit:
# https://greatexpectations.io/expectations/
APP_EXPECTATIONS = [
    {
        "expectation": "expect_column_values_to_be_increasing",
        "target_column": "column_1",
    },
    {
        "expectation": "expect_column_values_to_not_be_null",
        "target_column": "column_2",
    },
    {
        "expectation": "expect_column_sum_to_be_between",
        "target_column": "column_3",
        "args": {"min_value": 1, "max_value": 10},
    },
]

# Display proportions for columns containing expectation details.
EXPECTATION_COLUMN_SIZE = [1, 2, 5]

st.set_page_config(
    page_title="Proof-of-Concept Data Validator feat. Great Expectations",
    page_icon="🐣",
    initial_sidebar_state="expanded",
)

# Sidebar content.
st.sidebar.title("Proof-of-Concept Data Validator")
st.sidebar.markdown(
    "*featuring [**Great Expectations**](https://greatexpectations.io)*"
)

st.sidebar.markdown("---")
st.sidebar.write(
    """Modify the data table to see the resulting effect on data quality checks.
* Cell contents can be edited.
* Rows can be added and deleted."""
)

# Load requested sample data into an editable dataframe on the streamlit app.
sample_data = utils.get_sample_data("static_expectations_dataset.csv")
df_edited = st.data_editor(sample_data, num_rows="dynamic")

st.markdown("---")

# Create great expectations validator from the current state of the editable data.
validator = gx.from_pandas(df_edited)

# Display expectation column headers.
result_col, target_column_col, expectation_col = st.columns(EXPECTATION_COLUMN_SIZE)
result_col.markdown("**Validated**")
target_column_col.markdown("**Column**")
expectation_col.markdown("**Expectation**")

# Run and display defined expectations.
for expectation in APP_EXPECTATIONS:
    # Default expectation arguments to {} if not supplied.
    expectation_args = expectation.get("args", {})

    # Run the expectation with the GX validator on the target column, supplying any
    # provided arguments. Capture result for display.
    run_expectation = getattr(validator, expectation["expectation"])
    expectation_result = run_expectation(
        expectation["target_column"], **expectation_args
    )

    # Display expectation result and details.
    result_col, target_column_col, expectation_col = st.columns(EXPECTATION_COLUMN_SIZE)
    if expectation_result["success"]:
        result_col.success("", icon="✅")
    else:
        result_col.error("", icon="❌")

    target_column_col.text(expectation["target_column"])

    args_tooltip = f"***Expectation args:***  \n`{expectation_args}`"
    expectation_col.text(expectation["expectation"], help=args_tooltip)
