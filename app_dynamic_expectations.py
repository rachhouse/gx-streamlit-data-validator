"""Entrypoint Streamlit app file to run the proof-of-concept data validator with
dynamic expectations."""

from typing import Dict, List

import great_expectations as gx
import streamlit as st

import gx_streamlit_data_validator.utils as utils

# Define default expectations to be run and displayed in app output on load.
# For more expectations and expectation details, visit:
# https://greatexpectations.io/expectations/
DEFAULT_APP_EXPECTATIONS = [
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
EXPECTATION_COLUMN_SIZE = [1, 1, 2, 5]
NEW_EXPECTATION_DETAILS_COLUMN_SIZE = [2, 7]
NEW_EXPECTATION_PARAM_COLUMN_SIZE = [3, 4]


# Helper functions for app display and widgets.
def _delete_expectation(expectation_id: str) -> None:
    """Remove specified expectation from the app session state."""
    del st.session_state["expectations"][expectation_id]
    print(f"Deleted expectation {expectation_id} from session state")


def _create_new_expectation_param_widget_definition(
    param_column_proportions: List, params: List[Dict]
) -> List[Dict]:
    """Dynamically create input widgets for supplied expectation parameters, and return
    parameter metadata.

    Args:
        param_column_ratio: parameter widget columns proportions, as list
        params: List of dicts of parameter data, in the following format:
            [
                {
                    "param": "parameter name",
                    "default": "parameter default value",
                    "annotation": "parameter annotation",
                },
                ...
            ]

    Returns:
        List of dicts of param metadata, in the following format:
            [
                {
                    "name" : "param name",
                    "value" : param value,
                },
                ...
            ]
    """
    param_user_inputs = []

    for p in params:
        param_name_col, param_input_col = expectation_details_col.columns(
            param_column_proportions
        )
        param_name_col.text(p["param"])
        param_value = param_input_col.text_input(
            label=p["param"], key=f"input_{p['param']}", label_visibility="collapsed"
        )
        param_user_inputs.append(
            {
                "name": p["param"],
                "value": param_value,
            }
        )

    return param_user_inputs


def _add_new_expectation(
    expectation: str, expectation_target_col: str, expectation_args: List[Dict]
) -> None:
    """Add new expectation to session expectations.

    Args:
        expectation: string name of new expectation
        expectation_target_col: string name of new expectation target column
        expectation_args: list of dicts of new expectation arguments, in the following format:
            [
                {
                    "name" : "param name",
                    "value" : param value,
                },
                ...
            ]
    """
    formatted_expectation_args = {}

    for arg in expectation_args:
        if (arg["value"] == "") or (arg["value"] is None):
            continue

        arg_value = arg["value"].strip()

        if utils.is_int(arg["value"]):
            formatted_expectation_args[arg["name"]] = int(arg_value)
        elif utils.is_float(arg["value"]):
            formatted_expectation_args[arg["name"]] = float(arg_value)
        elif utils.is_bool(arg["value"]):
            formatted_expectation_args[arg["name"]] = utils.convert_to_bool(arg_value)
        else:
            formatted_expectation_args[arg["name"]] = arg_value

    st.session_state["expectations"][utils.get_expectation_uuid()] = {
        "expectation": expectation,
        "target_column": expectation_target_col,
        "args": formatted_expectation_args,
    }


##########################################################################
## BEGIN STREAMLIT APP ###################################################

st.set_page_config(
    page_title="Proof-of-Concept Data Validator feat. Great Expectations",
    page_icon="🐥",
    initial_sidebar_state="expanded",
)

# Sidebar content.
st.sidebar.title("Proof-of-Concept Data Validator")
st.sidebar.markdown(
    "*featuring [**Great Expectations**](https://greatexpectations.io)*"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """Modify the data table and expectations to see the resulting effect on data quality checks.
* Cell contents can be edited.
* Rows can be added and deleted.
* Expectations can be added and deleted.
"""
)
st.sidebar.markdown("")
st.sidebar.caption(
    """Note: Depending on the expectation, you may need to provide parameter values.
Accepted parameters have been restricted in an effort to improve app simplicity.
"""
)

# Load requested sample data into an editable dataframe on the streamlit app.
sample_data = utils.get_sample_data("static_expectations_dataset.csv")
df_edited = st.data_editor(sample_data, num_rows="dynamic")

st.markdown("---")

# Create great expectations validator from the current state of the editable data.
validator = gx.from_pandas(df_edited)

# Init default expectations for display.
if "expectations" not in st.session_state:
    st.session_state["expectations"] = utils.transform_expectations(
        DEFAULT_APP_EXPECTATIONS
    )

# Display expectation column headers.
add_drop_col, result_col, target_column_col, expectation_col = st.columns(
    EXPECTATION_COLUMN_SIZE
)
result_col.markdown("**Validated**")
target_column_col.markdown("**Column**")
expectation_col.markdown("**Expectation**")

# Run and display session expectations.
for expectation_id, expectation in st.session_state["expectations"].items():
    # Default expectation arguments to {} if not supplied.
    expectation_args = expectation.get("args", {})

    # Run the expectation with the GX validator on the target column, supplying any
    # provided arguments. Capture result for display.
    run_expectation = getattr(validator, expectation["expectation"])
    expectation_result = run_expectation(
        expectation["target_column"], **expectation_args
    )

    # Display expectation result and details.
    add_drop_col, result_col, target_column_col, expectation_col = st.columns(
        EXPECTATION_COLUMN_SIZE
    )

    # Add a button with a unique key and a callback to remove the expectation.
    add_drop_col.button(
        " ➖ ",
        key=f"drop_{expectation_id}",
        on_click=_delete_expectation,
        kwargs={"expectation_id": expectation_id},
    )

    if expectation_result["success"]:
        result_col.success("", icon="✅")
    else:
        result_col.error("", icon="❌")

    target_column_col.text(expectation["target_column"])

    args_tooltip = f"***Expectation args:***  \n`{expectation_args}`"
    expectation_col.text(expectation["expectation"], help=args_tooltip)

# Section to add new expectation to session expectations, with dynamic input widgets
# based on selected expectation.
add_drop_col, result_col, target_column_col, expectation_col = st.columns(
    EXPECTATION_COLUMN_SIZE
)

new_expectation = expectation_col.selectbox(
    "new_expectation",
    options=utils.get_available_expectations(validator),
    label_visibility="collapsed",
)

new_expectation_target_col = target_column_col.selectbox(
    "new_target_column", options=list(df_edited.columns), label_visibility="collapsed"
)

# Expectation param input, based on selected new_expectation.
_, expectation_details_col = st.columns(NEW_EXPECTATION_DETAILS_COLUMN_SIZE)

expectation_signature = utils.get_expectation_signature(validator, new_expectation)

with expectation_details_col.expander("Full Expectation Signature"):
    st.write(expectation_signature)

expectation_params = utils.get_expectation_parameters(expectation_signature)

dynamic_param_inputs = _create_new_expectation_param_widget_definition(
    NEW_EXPECTATION_PARAM_COLUMN_SIZE, expectation_params
)

add_drop_col.button(
    " ➕ ",
    on_click=_add_new_expectation,
    kwargs={
        "expectation": new_expectation,
        "expectation_target_col": new_expectation_target_col,
        "expectation_args": dynamic_param_inputs,
    },
)
