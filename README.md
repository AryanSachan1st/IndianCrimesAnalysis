# Indian Crime Analysis Dashboard

A Streamlit dashboard for analyzing and forecasting violent crime trials in Indian states using Facebook Prophet.

## Features

- Historical data visualization of violent crime trials by state
- Crime forecasting using Facebook Prophet model
- Year-over-year comparison analysis
- Crime type distribution visualization
- Seasonality analysis of crime patterns

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- Matplotlib
- Prophet
- Seaborn

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the dashboard with:
```
streamlit run app.py
```

## Dataset

The dashboard requires the `28_Trial_of_violent_crimes_by_courts.csv` dataset to function. This file should be placed in the same directory as `app.py`.

Note: The dataset is not included in this repository and needs to be uploaded separately.

## Branch Information

This repository uses the `main` branch as the default branch instead of the traditional `master` branch.
