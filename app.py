# ============================================
# Streamlit Crime Forecast Dashboard (India)
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
import seaborn as sns

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Crime Forecasting in India",
    page_icon="📊",
    layout="wide"
)

st.title("📈 Crime Forecasting Dashboard (India)")
st.markdown("""
Analyze and forecast (data available till 2010) **violent crime trials** in Indian states using **Facebook Prophet**.  
""")

# ---------- DATA READ ----------
df = pd.read_csv("28_Trial_of_violent_crimes_by_courts.csv")

# ---------- DATA CLEANING ----------
df.columns = df.columns.str.strip()
df = df.rename(columns={
    "Area_Name": "State",
    "Year": "Year",
    "Group_Name": "Crime_Group",
    "Trial_of_Violent_Crimes_by_Courts_Total": "Total_Crimes"
})
df["Total_Crimes"] = pd.to_numeric(df["Total_Crimes"], errors="coerce").fillna(0)

state_year = (
    df.groupby(["State", "Year"])["Total_Crimes"]
      .sum()
      .reset_index()
      .sort_values(["State", "Year"])
)

# ---------- SIDEBAR INPUT ----------
st.sidebar.header("🔍 Forecast Settings")
state_list = sorted(state_year["State"].unique())
selected_state = st.sidebar.selectbox("Select a State", state_list)
forecast_years = st.sidebar.slider("Forecast years into the future", 1, 10, 5)

# ---------- FUNCTION: FORECAST ----------
@st.cache_resource
def forecast_state(data, state_name, years=5):
    state_df = data[data["State"] == state_name][["Year", "Total_Crimes"]].copy()
    state_df.rename(columns={"Year": "ds", "Total_Crimes": "y"}, inplace=True)
    state_df["ds"] = pd.to_datetime(state_df["ds"], format="%Y")

    # --- Ensure enough data points ---
    if len(state_df) < 3:
        return None, None, None

    model = Prophet(yearly_seasonality=True)
    model.fit(state_df)

    future = model.make_future_dataframe(periods=years, freq='Y')
    forecast = model.predict(future)

    return state_df, forecast, model

# ---------- RUN FORECAST ----------
state_df, forecast, model = forecast_state(state_year, selected_state, forecast_years)
if forecast is None:
    st.warning(f"Not enough data points to forecast {selected_state}. Try another state.")
    st.stop()

# ---------- PLOTS ----------
st.subheader(f"📊 Historical & Forecasted Crime Trials for **{selected_state}**")

fig1 = model.plot(forecast)
plt.title(f"Forecast of Total Violent Crimes ({selected_state})")
plt.xlabel("Year")
plt.ylabel("Total Violent Crime Trials")
st.pyplot(fig1)
st.markdown("**Note:** The chart above shows both historical data points (black dots) and forecasted values (blue line) with confidence intervals (shaded area).")

# ---------- SEASONALITY ANALYSIS ----------
st.subheader("📅 Seasonality Analysis")
# Get the components from the model
try:
    # Extract components data
    trend = forecast[['ds', 'trend']]
    yearly = forecast[['ds', 'yearly']]
    
    # Calculate percentage changes for yearly seasonality
    # We'll calculate the percentage change relative to the mean of the yearly component
    mean_yearly = yearly['yearly'].mean()
    yearly['yearly_pct_change'] = ((yearly['yearly'] - mean_yearly) / abs(mean_yearly)) * 100 if mean_yearly != 0 else yearly['yearly']
    
    # Create custom plots with percentage changes
    fig2, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot trend component
    axes[0].plot(trend['ds'], trend['trend'])
    axes[0].set_title('Overall Trend')
    axes[0].set_ylabel('Crime Trials')
    
    # Plot yearly seasonality as percentage change
    axes[1].plot(yearly['ds'], yearly['yearly_pct_change'])
    axes[1].set_title('Yearly Seasonality (Percentage Change from Yearly Average)')
    axes[1].set_ylabel('Percentage Change (%)')
    axes[1].set_xlabel('Day of Year')
    
    # Add horizontal line at y=0 for reference
    axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    st.pyplot(fig2)
    
    # Display interpretation
    st.markdown("**Interpretation:**")
    st.markdown("- The top chart shows the overall trend in crime trials over time.")
    st.markdown("- The bottom chart shows how crime rates fluctuate throughout the year as a percentage change from the yearly average.")
    st.markdown("- Values above 0% indicate periods when crime is higher than the yearly average, and values below 0% indicate periods when crime is lower than the yearly average.")
    
except Exception as e:
    st.warning("Could not display seasonality components.")
    st.markdown("**Interpretation:** These charts show the seasonal patterns in the data. The yearly trend shows how crime rates typically fluctuate throughout the year as a percentage change from the yearly average, while the overall trend shows how crime rates have changed over the entire time period.")

# ---------- YEAR-OVER-YEAR COMPARISON ----------
st.subheader("🔄 Year-over-Year Comparison")
# Calculate year-over-year percentage change
state_df_copy = state_df.copy()
state_df_copy["Year"] = state_df_copy["ds"].dt.year
state_df_copy["YoY_Change"] = state_df_copy["y"].pct_change() * 100

# Create bar chart for YoY changes
fig3, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=state_df_copy.dropna(), x="Year", y="YoY_Change", ax=ax, palette="viridis")
ax.set_title(f"Year-over-Year Percentage Change ({selected_state})")
ax.set_xlabel("Year")
ax.set_ylabel("Percentage Change (%)")
plt.xticks(rotation=45)
st.pyplot(fig3)

# Display the data in a table format as well
st.dataframe(state_df_copy[["Year", "y", "YoY_Change"]].dropna().style.format({
    "y": "{:.0f}",
    "YoY_Change": "{:.1f}%"
}).background_gradient(cmap="RdYlGn", subset=["YoY_Change"]))

st.markdown("**Interpretation:** This chart shows the percentage change in violent crime trials from one year to the next. Green bars indicate an increase in crime trials, while red bars indicate a decrease.")

# ---------- CRIME TYPE DISTRIBUTION ----------
st.subheader("⚖️ Crime Type Distribution")
# Get latest data for crime type distribution
latest_year = df["Year"].max()
crime_type_data = df[(df["State"] == selected_state) & (df["Year"] == latest_year)]

if not crime_type_data.empty:
    crime_type_totals = crime_type_data.groupby("Crime_Group")["Total_Crimes"].sum().reset_index()
    crime_type_totals = crime_type_totals[crime_type_totals["Total_Crimes"] > 0].sort_values("Total_Crimes", ascending=False)
    
    # Create pie chart for crime type distribution (without autopct to prevent overlapping)
    fig4, ax = plt.subplots(figsize=(10, 8))
    
    # If there are many crime types, use a legend instead of labels to prevent overlapping
    if len(crime_type_totals) > 5:
        wedges, texts = ax.pie(crime_type_totals["Total_Crimes"], startangle=90)
        ax.legend(wedges, crime_type_totals["Crime_Group"], title="Crime Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    else:
        wedges, texts = ax.pie(crime_type_totals["Total_Crimes"], labels=crime_type_totals["Crime_Group"], startangle=90)
    
    ax.set_title(f"Crime Type Distribution in {selected_state} ({latest_year})")
    plt.tight_layout()
    st.pyplot(fig4)
    
    # Calculate percentages for display
    crime_type_totals["Percentage"] = (crime_type_totals["Total_Crimes"] / crime_type_totals["Total_Crimes"].sum()) * 100
    
    # Display data in table format with percentages
    st.dataframe(crime_type_totals[["Crime_Group", "Total_Crimes", "Percentage"]].style.format({
        "Total_Crimes": "{:.0f}",
        "Percentage": "{:.1f}%"
    }).background_gradient(cmap="Blues", subset=["Total_Crimes"]))
else:
    st.info("No crime type data available for the selected state and year.")

st.markdown("**Interpretation:** This pie chart shows the distribution of different types of violent crimes in the selected state for the most recent year in the dataset.")

# ---------- FORECAST SUMMARY ----------
# Extract future forecast data (beyond the last historical data point)
last_historical_year = state_df["ds"].max()
forecast_future = forecast[forecast["ds"] > last_historical_year][["ds", "yhat", "yhat_lower", "yhat_upper"]]

if not forecast_future.empty:
    st.subheader("🔹 Forecast Summary")
    # Convert datetime to year for display
    forecast_future_display = forecast_future.copy()
    forecast_future_display["ds"] = forecast_future_display["ds"].dt.year
    # Rename columns for clarity
    forecast_future_display.rename(columns={
        "ds": "Year",
        "yhat": "Predicted Crimes",
        "yhat_lower": "Lower Bound",
        "yhat_upper": "Upper Bound"
    }, inplace=True)
    # Format numbers to be more readable
    st.dataframe(forecast_future_display.style.format({
        "Predicted Crimes": "{:.0f}",
        "Lower Bound": "{:.0f}",
        "Upper Bound": "{:.0f}"
    }).background_gradient(cmap="YlOrRd"))
    st.markdown("**Interpretation:** The table shows predicted crime counts with a confidence interval.")
    st.markdown("**Note:** This table shows only the forecasted values, not the historical data. The years shown are predictions for future years beyond the last data point in the historical dataset.")
else:
    st.info("⚠️ No future forecast data available. Try increasing the forecast years.")

# ---------- TREND VISUALIZATION ----------
st.subheader("📉 Historical Trend")
fig2, ax = plt.subplots(figsize=(8, 4))
sns.lineplot(data=state_df, x="ds", y="y", marker="o", ax=ax)
ax.set_title(f"Historical Violent Crime Trend ({selected_state})")
ax.set_xlabel("Year")
ax.set_ylabel("Total Crimes")
st.pyplot(fig2)

# ---------- INSIGHTS ----------
if forecast is not None and not forecast.empty and not forecast_future.empty:
    # Get the latest historical value and the first forecast value for comparison
    latest = state_df["y"].iloc[-1]
    pred_first_future = forecast_future["yhat"].iloc[0]
    change = ((pred_first_future - latest) / latest * 100) if latest > 0 else 0

    st.subheader("🧠 Insights")
    if change > 5:
        st.warning(f"⚠️ Projected increase of **{change:.1f}%** in total violent-crime trials.")
    elif change < -5:
        st.success(f"✅ Projected decrease of **{abs(change):.1f}%**.")
    else:
        st.info(f"ℹ️ Crime trials are expected to remain relatively stable (~{change:.1f}%).")
else:
    if forecast is None or forecast.empty:
        st.warning("No forecast data available for this selection.")
    elif forecast_future.empty:
        st.info("Not enough forecast data to generate insights.")

# ---------- OPTIONAL: CRIME TYPE FORECAST ----------
st.sidebar.markdown("---")
st.sidebar.subheader("Per Crime Type Forecast (Optional)")
crime_groups = sorted(df["Crime_Group"].unique())
selected_crime = st.sidebar.selectbox("Select Crime Group", crime_groups)

if st.sidebar.button("Run Forecast for Crime Type"):
    group_df = df[(df["State"] == selected_state) & (df["Crime_Group"] == selected_crime)]
    if len(group_df) > 2:
        grp_df = group_df.groupby("Year")["Total_Crimes"].sum().reset_index()
        grp_df.rename(columns={"Year": "ds", "Total_Crimes": "y"}, inplace=True)
        grp_df["ds"] = pd.to_datetime(grp_df["ds"], format="%Y")
        model2 = Prophet(yearly_seasonality=True)
        model2.fit(grp_df)
        future2 = model2.make_future_dataframe(periods=forecast_years, freq='Y')
        forecast2 = model2.predict(future2)
        st.subheader(f"🔸 Forecast for {selected_crime} in {selected_state}")
        fig3 = model2.plot(forecast2)
        st.pyplot(fig3)
    else:
        st.warning("Not enough data points for this crime type in this state.")
