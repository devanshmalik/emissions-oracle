# Appendix

This page aims to provide details on the methodologies used and assumptions made for various aspects of the project. This includes:
- Data Science End-to-End Pipeline (data collection, preprocessing, feature engineering, modelling, reporting)
- Greenhouse Gas (GHG) Emissions (emissions calculations, assumptions, etc.)
- Project Assumptions (electricity generation context related assumptions)

## 1. Data Science Pipeline

The project was structured to easily allow the end to end running of data science pipeline through an interface.
To create modular components that feed into each other, both the data and python scripts were separated into multiple layers.

**The different data layers are:**

**Raw**
  - The data pulled from the external source is the raw data. Raw data is immutable and is never edited. This allows for anyone to be able to reproduce the final products with only the python code and the raw data.
  - For this project, all data was pulled from the US Energy Information Administration which is committed to open data by making it free and available through an Application Programming Interface (API).

**Intermediate**
  - If the raw data is messy, it is advisable to create an intermediate layer that consists of tidy copies of raw data. We should not combine different data sets or create calculated fields in this layer.
  - For this project, this stage involved two main steps:
    - For successful API requests, convert raw data in JSON format to CSV and impute any missing time periods with a value of 0
    - For unsuccessful API requests, it implies there is no electricity generation for the specific type and thus creating an empty CSV with 0 for every time period.

**Processed**
  - To perform the modelling work, the input data needs to be combined and enriched by creating features. The data sets created in this process are stored in the processed layer and are ready to be used as input into machine learning algorithms.
  - For this project, most of the electricity generation data mapped directly to a feature of the same type without any transformations. For example, API output for coal generation mapped directly to a feature for coal generation by time.
  - The only engineered feature was "Other" category of electricity generation with the following calculation:
    - `other_generation = other_renewables_generation - wind_generation - solar_utility_generation + EIA_other_generation`
    - This calculation was based on research into which generation sources fall under each label in the [EIA Electricity Generation data](https://www.eia.gov/electricity/annual/html/epa_03_01_a.html).
    - Note: The calculated feature `other_generation` is different from the `Other` imported from EIA directly.

**Models**
  - The processed data is used to train predictive models, explanatory models, etc. The trained models are stored in the model layer.
  - For this project, this layer contains all the time-series forecasting models (specifically [Facebook Prophet](https://facebook.github.io/prophet/) models).
    - There are 10 Prophet models for each region (one for each type of electricity generation / fuel consumption)


**Model Output**
  - Model performance metrics, model selection information and predictions are kept in the model output layer.

**Reporting**
  - Reporting can be performed across the pipeline. This layer can contain data in numerous formats to aid in the sharing of relevant insights.
  - For this project, there are three main types of reporting data that is used to power the Streamlit Web Application:
    - **Individual Forecasts**: This folder contains forecasts for each Prophet model separately, thus one forecast for each type of generation source.
    - **Combined Forecasts**: This folder combines the data from individual forecasts to create one CSV each for each region. For example, the Net Electricity Generation CSV for Alabama will contain one column for every type of generation source along with a date column.
    - **Emission Forecasts**: This folder contains GHG emissions estimates for all the electricity generation in each region. The two types of emissions data is:
      - Emissions Intensity: This is the volume of GHG emissions per unit of electricity generated. Hence, the lower the emissions intensity, the greener the electricity grid. This value allows for easier comparison of emissions between regions compared to using "Total Emissions".
      - Total Emissions: This is the volume of total GHG emissions for the chosen electricity generation source.

### Pipeline Interface

A higher level interface has also been created to easily re-run any specific component of the data pipeline above without affecting
other modular components.

This is done through a python class called `PipelineInterface` and sample code to run any pipeline component is:
```python
interface = PipelineInterface(EIA_API_IDS_YML_FILEPATH, EMISSIONS_FACTORS_YML_FILEPATH)
interface.pull_data()
interface.clean_data()
interface.process_data()
interface.train_models()
interface.create_forecasts()
interface.calculate_emissions()
```

## 2. Greenhouse Gas Emissions Estimate Methodology

All estimates in this analysis are aimed to account for the entire life cycle of the electricity generation.
The Life Cycle Assessments (LCA) help quantify the environmental burdens from "cradle to grave" and facilitate more-consistent comparisons of energy technologies.

Generalized life cycle stages for each energy technology include:
1. **Upstream**: Resource Extraction, Material Manufacturing, Component Manufacturing, Construction
2. **Fuel Cycle**: Resource Extraction / Production, Processing / Conversion, Delivery to Site
3. **Operation**: Combustion, Maintenance, Operation
4. **Downstream**: Dismantling, Decommissioning, Disposal and Recycling

The proportion of GHG emissions from each lifecycle stage differs by technology:
  - For fossil-fueled technologies, fuel combustion during operation of the facility emits the vast majority of GHGs.
  - For nuclear and renewable energy technologies, most GHG emissions occur upstream of operation.


### Emissions Factors

An Emissions Factor is a representative value that attempts to relate the quantity of GHG emissions released to the
atmosphere with the amount of electricity generated by a certain source (can be any activity that releases GHG emissions).
  - For example: Nuclear Power has a Total Life Cycle Emissions Factor of 13 kg CO2e per MWh of electricity generated (source: NREL).
    This means that for every MWh of electricity generated, Nuclear Power releases 13 kilograms of CO2 equivalent GHG emissions.
  - CO2 "Equivalent" emissions is a metric used to compare the emissions from various GHGs on the basis of their global-warming potential (GWP).
    Basically, not every GHG contributes equally to global warming. For example: Methane has a GWP of 25 which means that 1 kg of Methane is equivalent to 25 kg of Carbon Dioxide in the atmosphere.

**The biggest caveat when working with emissions factors values is that they can differ drastically based on tons of factors considered within the specific study.**
Thus, to **reliably** estimate the GHG emissions for each energy source, GHG emissions factors were obtained from the [Life Cycle Assessment Harmonization Project](https://www.nrel.gov/analysis/life-cycle-assessment.html)
by the National Renewable Energy Laboratory (NREL) that considered approximately 3,000 published life cycle assessment studies on utility-scale electricity generation.

#### Special Cases: Coal and Natural Gas

As mentioned earlier, fuel combustion during operation is the vast majority of GHGs for fossil-fueled generation. Instead of using the median emissions factors values for Coal and Natural Gas for the Combustion stage
from the NREL study above, a more accurate method was utilized.
- From the EIA API, fuel consumption data for both coal and natural gas was pulled for each state. This data represents the amount of heat from the specified fuel used for electricty generation.
- Emissions factors for each fuel were pulled from another API called [ClimatIQ](https://docs.climatiq.io/) which hosts an [Open Emission Factor Database](https://github.com/climatiq/Open-Emission-Factors-DB).

This approach is more accurate because every coal / natural gas generation plant has a different efficiency in how much fuel is needed to generate a unit of electricity. Thus, by using the exact amount of
fuel used (instead of the final amount of electricity generated), we're able to more accurately estimate the associated GHG emissions.


## 3. Project Assumptions

With any machine learning project, there are always assumptions associated with any decision made throughout the training process.
The forecasted electricity generation and emissions for each region / generation source make many implicit assumptions
that are not reflective of the real world.

Some of these assumptions include:
- Lack of data on Power Purchase Agreements(PPA), life of electricity generation assets such as Nuclear Power Plant refurbishments / shutdown, signing of new PPAs for certain technologies, etc.
- Worldwide factors affecting energy demand such as Covid-19 Pandemic, War in Ukraine, etc.
- New policies coming into affect (either discouraging dirty fuels or boosting greener generation sources)
- And many more...

Hence, any of the forecasted estimates in this analysis should be taken with a grain of salt.
