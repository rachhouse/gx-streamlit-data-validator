"""Helper functions for the data validator streamlit app files."""

import pathlib

import pandas as pd

SAMPLE_DATA_DIR = pathlib.Path(__file__).parent / "sample_data"


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
