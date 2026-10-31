import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Name', 'Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce')

    return gdp_df


def calculate_annual_gdp_growth(gdp_data, start_year, end_year):
    """Calculate nominal annual GDP growth only from adjacent, positive observations."""
    growth_df = gdp_data[
        ['Country Name', 'Country Code', 'Year', 'GDP']
    ].copy().sort_values(['Country Code', 'Year'])
    growth_df['GDP'] = pd.to_numeric(growth_df['GDP'], errors='coerce')

    country_groups = growth_df.groupby('Country Code')
    growth_df['Previous GDP'] = country_groups['GDP'].shift()
    growth_df['Previous Year'] = country_groups['Year'].shift()

    valid_observations = (
        (growth_df['Year'] == growth_df['Previous Year'] + 1)
        & (growth_df['GDP'] > 0)
        & (growth_df['Previous GDP'] > 0)
    )
    growth_df = growth_df[
        valid_observations
        & (growth_df['Year'] >= start_year)
        & (growth_df['Year'] <= end_year)
    ].copy()
    growth_df['Annual nominal GDP growth (%)'] = (
        growth_df['GDP'] / growth_df['Previous GDP'] - 1
    ) * 100

    return growth_df


gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''

st.header('GDP growth comparison', divider='gray')

country_options = list(countries)
first_country_default = country_options.index('DEU') if 'DEU' in country_options else 0
first_country = st.selectbox(
    'First country',
    country_options,
    index=first_country_default,
)

second_country_options = [country for country in country_options if country != first_country]
second_country_default = (
    second_country_options.index('FRA') if 'FRA' in second_country_options else 0
)
second_country = st.selectbox(
    'Second country',
    second_country_options,
    index=second_country_default,
)

comparison_gdp_df = gdp_df[
    gdp_df['Country Code'].isin([first_country, second_country])
].sort_values(['Country Code', 'Year']).copy()
comparison_gdp_df['GDP Growth (%)'] = (
    comparison_gdp_df.groupby('Country Code')['GDP'].pct_change(fill_method=None) * 100
)
comparison_gdp_df = comparison_gdp_df[
    (comparison_gdp_df['Year'] >= from_year)
    & (comparison_gdp_df['Year'] <= to_year)
]

st.line_chart(
    comparison_gdp_df,
    x='Year',
    y='GDP Growth (%)',
    color='Country Code',
)


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )

st.header('Growth and Economic Stability', divider='gray')

st.info(
    'The available indicator is GDP (current US$), which is nominal GDP. '
    'It includes the effects of inflation and exchange-rate movements, so it '
    'cannot be used to calculate real GDP growth. The results below are '
    'explicitly labeled nominal GDP growth and should not be interpreted as '
    'real economic growth.'
)

st.caption(
    f'Growth rates are calculated for ending years {from_year}–{to_year} '
    'against the immediately preceding calendar year. Missing values, zero '
    'or negative GDP observations, and non-consecutive years are excluded. '
    'Volatility is the population standard deviation of the available annual '
    'rates; the observation count is shown in the summary.'
)

annual_growth_df = calculate_annual_gdp_growth(gdp_df, from_year, to_year)

if annual_growth_df.empty:
    st.warning(
        'There are no valid consecutive, positive GDP observations for this '
        'period. Choose a wider year range to see growth statistics.'
    )
else:
    growth_summary = annual_growth_df.groupby(
        ['Country Name', 'Country Code'], as_index=False
    ).agg(
        **{
            'Mean annual nominal GDP growth (%)': (
                'Annual nominal GDP growth (%)',
                'mean',
            ),
            'Nominal GDP growth volatility (percentage points)': (
                'Annual nominal GDP growth (%)',
                lambda values: values.std(ddof=0),
            ),
            'Valid annual observations': (
                'Annual nominal GDP growth (%)',
                'count',
            ),
        }
    ).sort_values('Country Name')

    country_labels = dict(zip(
        growth_summary['Country Code'],
        growth_summary['Country Name'],
    ))
    selected_growth_country = st.selectbox(
        'Country for annual growth details',
        growth_summary['Country Code'].tolist(),
        format_func=lambda code: f'{country_labels[code]} ({code})',
    )

    st.subheader('Nominal GDP growth: mean and volatility')
    scatter_data = growth_summary.copy()
    scatter_data['Selection'] = scatter_data['Country Code'].map(
        lambda code: (
            'Selected country'
            if code == selected_growth_country
            else 'Other countries'
        )
    )
    st.scatter_chart(
        scatter_data,
        x='Nominal GDP growth volatility (percentage points)',
        y='Mean annual nominal GDP growth (%)',
        color='Selection',
        x_label='Growth volatility (percentage points)',
        y_label='Mean annual nominal GDP growth (%)',
        alt=(
            'Scatterplot of nominal GDP growth volatility against mean annual '
            'nominal GDP growth, with the selected country highlighted.'
        ),
    )

    st.subheader('Nominal GDP growth summary by country')
    st.dataframe(
        growth_summary,
        hide_index=True,
        width='stretch',
    )

    st.subheader(
        f'Annual nominal GDP growth: {country_labels[selected_growth_country]}'
    )
    selected_annual_growth = annual_growth_df[
        annual_growth_df['Country Code'] == selected_growth_country
    ][['Year', 'Annual nominal GDP growth (%)']].sort_values('Year')
    st.dataframe(
        selected_annual_growth,
        hide_index=True,
        width='stretch',
    )
