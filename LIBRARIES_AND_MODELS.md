# Libraries and Models Used in Crime Forecasting Dashboard

## Overview
This document explains the working of the libraries and models used in the Streamlit crime forecasting dashboard for analyzing and predicting violent crime trials in Indian states.

## Libraries Used

### 1. Streamlit
Streamlit is the core framework used to build the web application interface.

**Usage in the project:**
- Creating the dashboard layout with `st.set_page_config()`
- Displaying titles, headers, and markdown text
- Implementing interactive widgets like selectbox and slider in the sidebar
- Caching the forecasting function with `@st.cache_resource` decorator
- Rendering plots with `st.pyplot()`
- Displaying dataframes with `st.dataframe()`
- Showing warning and info messages to users

### 2. Pandas
Pandas is used for data manipulation and analysis throughout the application.

**Usage in the project:**
- Reading CSV data with `pd.read_csv()`
- Data cleaning operations like stripping column names and renaming columns
- Converting data types with `pd.to_numeric()`
- Grouping data by state and year with `groupby()`
- Creating copies of dataframes for processing
- Date conversion with `pd.to_datetime()`
- Calculating percentage changes with `pct_change()`

### 3. Matplotlib
Matplotlib is used for basic plotting functionality, particularly with the Prophet model's built-in plotting.

**Usage in the project:**
- Creating figures and plots through Prophet's `model.plot()`
- Setting plot titles, axis labels
- Displaying plots in Streamlit with `st.pyplot()`

### 4. Prophet
Facebook Prophet is the main forecasting model used to predict future crime trends.

**Usage in the project:**
- Creating a Prophet model instance with `Prophet(yearly_seasonality=True)`
- Training the model with historical data using `model.fit()`
- Generating future dates for forecasting with `model.make_future_dataframe()`
- Making predictions with `model.predict()`
- Creating forecast plots with `model.plot()`
- Extracting model components like trend and seasonality

**How it works:**
Prophet is a procedure for forecasting time series data based on an additive model where non-linear trends are fit with yearly, weekly, and daily seasonality, plus holiday effects. It works best with time series that have strong seasonal effects and several seasons of historical data.

In this project, Prophet:
1. Takes historical crime data (year and total crimes)
2. Fits a model to identify trends and patterns
3. Forecasts future crime rates for a specified number of years
4. Provides confidence intervals for predictions

### 5. Seaborn
Seaborn is used for creating more visually appealing statistical plots.

**Usage in the project:**
- Creating bar plots for year-over-year comparison with `sns.barplot()`
- Creating line plots for historical trends with `sns.lineplot()`
- Applying color palettes to visualizations

## Data Flow and Processing

1. **Data Loading**: The application loads crime data from `28_Trial_of_violent_crimes_by_courts.csv`
2. **Data Cleaning**: Column names are standardized and data types are converted
3. **Data Aggregation**: Crime data is grouped by state and year
4. **User Input**: Users select a state and forecast period through Streamlit sidebar widgets
5. **Forecasting**: Prophet model generates predictions for the selected state
6. **Visualization**: Multiple charts are created to show historical trends, forecasts, and crime type distributions
7. **Insights**: The application provides interpretations of the data and forecasts

## Key Components

### Forecasting Function
```python
@st.cache_resource
def forecast_state(data, state_name, years=5):
    # Filters data for selected state
    # Renames columns to match Prophet's requirements (ds for date, y for value)
    # Creates and trains Prophet model
    # Generates future dataframe and predictions
    # Returns processed data, forecast, and model
```

### Visualizations
- **Forecast Plot**: Shows historical data points and predicted values with confidence intervals
- **Seasonality Analysis**: Displays trend components and yearly seasonality patterns
- **Year-over-Year Comparison**: Bar chart showing percentage changes in crime rates
- **Crime Type Distribution**: Pie chart showing distribution of different crime types
- **Historical Trend**: Line plot showing crime trends over time

## Model Interpretation Features
The dashboard provides automated interpretation of:
- Forecast trends (increasing, decreasing, or stable)
- Seasonality components
- Year-over-year changes
- Crime type distributions
