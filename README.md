# :earth_americas: GDP dashboard template

A simple Streamlit app showing the GDP of different countries in the world.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gdp-dashboard-template.streamlit.app/)

### Growth and Economic Stability

The dashboard compares mean annual GDP growth and growth volatility over the
selected year range, and shows annual rates for a selected country. The included
World Bank series is **GDP (current US$)**, which is nominal GDP; it is not
inflation-adjusted real GDP. Growth figures in this section are therefore
labeled nominal and should not be interpreted as real economic growth.

Rates are calculated only when both adjacent calendar years have positive,
non-missing GDP observations. The summary reports the mean and population
standard deviation of the available annual rates.

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
