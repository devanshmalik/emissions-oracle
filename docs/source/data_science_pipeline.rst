Data Science Pipeline
==========================

This page aims to provide details on the methodologies used and assumptions made for the Data Science End-to-End Pipeline (data collection, preprocessing, feature engineering, modelling, reporting).

Data Layers
-------------

The project was structured to easily allow the end to end running of data science pipeline through an interface.
To create modular components that feed into each other, both the data and python scripts were separated into multiple layers. The different data layers are described below.

Raw
^^^^^^^

- The data pulled from the external source is the raw data. Raw data is immutable and is never edited. This allows for anyone to be able to reproduce the final products with only the python code and the raw data.
- For this project, all data was pulled from the US Energy Information Administration which is committed to open data by making it free and available through an Application Programming Interface (API).

Intermediate
^^^^^^^^^^^^^^
- If the raw data is messy, it is advisable to create an intermediate layer that consists of tidy copies of raw data. We should not combine different data sets or create calculated fields in this layer.
- For this project, this stage involved two main steps:

  - For successful API requests, convert raw data in JSON format to CSV and impute any missing time periods with a value of 0
  - For unsuccessful API requests, it implies there is no electricity generation for the specific type and thus creating an empty CSV with 0 for every time period.

Processed
^^^^^^^^^^^^^^

- To perform the modelling work, the input data needs to be combined and enriched by creating features. The data sets created in this process are stored in the processed layer and are ready to be used as input into machine learning algorithms.
- For this project, most of the electricity generation data mapped directly to a feature of the same type without any transformations. For example, API output for coal generation mapped directly to a feature for coal generation by time.
- The only engineered feature was "Other" category of electricity generation with the following calculation:

  - ``other_generation = other_renewables_generation - wind_generation - solar_utility_generation + EIA_other_generation``
  - This calculation was based on research into which generation sources fall under each label in the `EIA Electricity Generation data <https://www.eia.gov/electricity/annual/html/epa_03_01_a.html>`_.
  - Note: The calculated feature `other_generation` is different from the `Other` imported from EIA directly.

Models
^^^^^^^^^^^^^^

- The processed data is used to train predictive models, explanatory models, etc. The trained models are stored in the model layer.
- For this project, this layer contains all the time-series forecasting models (specifically `Facebook Prophet <https://facebook.github.io/prophet/>`_ models).

  - There are 10 Prophet models for each region (one for each type of electricity generation / fuel consumption)

Model Output
^^^^^^^^^^^^^^

- Model performance metrics, model selection information and predictions are kept in the model output layer.

Reporting
^^^^^^^^^^^^^^
- Reporting can be performed across the pipeline. This layer can contain data in numerous formats to aid in the sharing of relevant insights.
- For this project, there are three main types of reporting data that is used to power the Streamlit Web Application:

  - **Individual Forecasts**: This folder contains forecasts for each Prophet model separately, thus one forecast for each type of generation source.
  - **Combined Forecasts**: This folder combines the data from individual forecasts to create one CSV each for each region. For example, the Net Electricity Generation CSV for Alabama will contain one column for every type of generation source along with a date column.
  - **Emission Forecasts**: This folder contains GHG emissions estimates for all the electricity generation in each region. The two types of emissions data is:

    - Emissions Intensity: This is the volume of GHG emissions per unit of electricity generated. Hence, the lower the emissions intensity, the greener the electricity grid. This value allows for easier comparison of emissions between regions compared to using "Total Emissions".
    - Total Emissions: This is the volume of total GHG emissions for the chosen electricity generation source.

Pipeline Interface
-----------------------

A higher level interface has also been created to easily re-run any specific component of the data pipeline above without affecting
other modular components.

This is done through a python class called ``PipelineInterface`` and sample code to run any pipeline component is:

.. code-block::

    interface = PipelineInterface(EIA_API_IDS_YML_FILEPATH, EMISSIONS_FACTORS_YML_FILEPATH)
    interface.pull_data()
    interface.clean_data()
    interface.process_data()
    interface.train_models()
    interface.create_forecasts()
    interface.calculate_emissions()