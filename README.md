# gx-streamlit-data-validator

This repo hosts a simple, interactive, proof-of-concept data validator application built using [Streamlit](https://streamlit.io) and [Great Expectations](https://greatexpectations.io/gx-oss).

## How to Run the App
This app uses [Poetry](https://python-poetry.org) for dependency & environment management; the run instructions below assume you have [Poetry installed](https://python-poetry.org/docs/#installation).

There are two versions of the app that you can choose to run:
* `app_static_expectations.py`. This version implements a static (hardcoded) set of expectations that cannot be altered.
* `app_dynamic_expectations.py`: This version allows you to add and remove expectations within the running app.

To run the app:
1. `git clone` this repo to your local machine.
1. `cd` to the root folder of this cloned repo.
1. Run `poetry install` to install project dependencies.
1. From the root folder of this cloned repo, start your chosen app version using one of the following:
   * `poetry run streamlit run app_static_expectations.py`
   * `poetry run streamlit run app_dynamic_expectations.py`
1. You can then access the app UI through a web browser using the URL displayed by the Streamlit command output, typically: `http://localhost:8501`

## Known Issues/Caveats

This app is a proof-of-concept and thus does not have robust error handling. If you are using the dynamic expectations version of the app, depending on the expectations that you try to add and the data in the editable dataframe, things might break. I've tested with a number of the simpler column expectations (e.g. `expect_column_max_to_be_between`, `expect_column_to_exist`, etc.), but have not exhaustively tested adding all the possible expectations. Some of the expectations with more complicated input parameters, e.g. `expect_column_bootstrapped_ks_test_p_value_to_be_greater_than`, will require additional development work to type check and appropriately cast user input.

And, on the subject of possible expectations - the dynamic expectations version of the app uses `inspect` both to generate the list of possible expectations that can be added and to determine the necessary input parameters for an individual expectation. You will see that there are often fewer input argument widgets than the full list of possible parameters in the expectation method signature.
I've restricted a number of the common optional parameters in an effort to simplify the visual interface of the app.