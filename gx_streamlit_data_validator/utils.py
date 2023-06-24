"""Helper functions for the data validator streamlit app files."""

import inspect
import pathlib
import uuid
from typing import Dict, List

import great_expectations as gx
import pandas as pd

SAMPLE_DATA_DIR = pathlib.Path(__file__).parent / "sample_data"

# List of expectation parameters to ignore when building dynamic input widgets.
IGNORE_EXPECTATION_PARAMS = [
    "self",
    "column",
    "column_index",
    "meta",
    "catch_exceptions",
    "include_config",
    "result_format",
    "output_strftime_format",
    "parse_strings_as_datetimes",
    "strict_min",
    "strict_max",
]


def get_sample_data(dataset_filename: str) -> pd.DataFrame:
    """Load and return sample data.

    Args:
        dataset_name: File name of requested dataset in SAMPLE_DATA_DIR,
            e.g. static_expectations_dataset.csv

    Returns:
        Data from requested file, as pandas DataFrame
    """
    try:
        df = pd.read_csv(SAMPLE_DATA_DIR / dataset_filename)
        return df
    except:
        raise Exception(f"Unable to ingest requested dataset file: {dataset_filename}")


def get_expectation_uuid() -> str:
    """Return random uuid as string."""
    return str(uuid.uuid4())


def transform_expectations(source_expectations: List[Dict]) -> Dict:
    """Transform GX expectation data for use in dynamic data validator app.

    Args:
        source_expectations: Expectation data as list of dicts, in the following format:
        [
            {
                "expectation" : "expectation name",
                "target_column" : "column name",
                "args" : {...}
            },
            ...
        ]

    Returns:
        Dict of transformed expectation data, keyed on expectation uuid,
        in the following format:
        {
            "uuid-1" : {
                "expectation" : "expectation name",
                "target_column" : "column name",
                "args" : {...}
            },
            "uuid-2" : {...},
            ...
        }
    """
    transformed_expectations = {}

    for expectation in source_expectations:
        expectation_uuid = get_expectation_uuid()
        transformed_expectations[expectation_uuid] = expectation

    return transformed_expectations


def get_available_expectations(
    validator: gx.dataset.pandas_dataset.PandasDataset,
) -> List[str]:
    """Return a list of GX expectations that can be run on the supplied validator.

    Args:
        validator: great_expectations validator for pandas DataFrame

    Returns:
        List of valid expectations, by name
    """
    return [
        x[0] for x in inspect.getmembers(validator) if x[0].startswith("expect_column")
    ]


def get_expectation_signature(
    validator: gx.dataset.pandas_dataset.PandasDataset, expectation: str
) -> inspect.Signature:
    """Return the method signature of the specified expectation.

    Args:
        validator: great_expectations validator for pandas DataFrame
        expectation: string name of expectation

    Returns:
        Signature of specified expectation, as inspect.Signature object
    """
    return inspect.signature(getattr(validator, expectation))


def get_expectation_parameters(signature: inspect.Signature) -> List[Dict]:
    """Return parameters, from the supplied method signature, to use for dynamically
    creating expectation input.

    Args:
        signature: method signature, as inspect.Signature object

    Returns:
        List of dicts of parameter metadata, in the following format:
        [
            {
                "param": "parameter name",
                "default": "parameter default value",
                "annotation": "parameter annotation",
            },
            ...
        ]

    """
    expectation_params = []

    for param_name, param_spec in signature.parameters.items():
        if param_name in IGNORE_EXPECTATION_PARAMS:
            continue

        expectation_params.append(
            {
                "param": param_name,
                "default": param_spec.default,
                "annotation": param_spec.annotation,
            }
        )

    return expectation_params


def is_float(x: str) -> bool:
    """Returns bool indicating if supplied string can be cast to a float."""
    try:
        float(x)
        return True
    except:
        return False


def is_int(x: str) -> bool:
    """Returns bool indicating if supplied string can be cast to an int."""
    try:
        int(x)
        return True
    except:
        return False


def is_bool(x: str) -> bool:
    """Returns bool indicating if supplied string can be cast to a bool."""
    try:
        if (x.lower() == "false") or (x.lower() == "true"):
            return True
        else:
            return False
    except:
        return False


def convert_to_bool(x: str) -> bool:
    """Convert string representation of bool to actual bool."""
    if x.lower() == "false":
        return False
    elif x.lower() == "true":
        return True
    else:
        ValueError(
            "Supplied string should either be 'true' or 'false' (case insensitive)"
        )
