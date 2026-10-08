import pandas as pd

# Step 1 - Fetch mortage data from FRED 
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# Step 2 – Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

# Step 3 – Create a matching year_month key on the MLS datasets
df_sold = pd.read_csv("All_Months_Sold.csv")
df_listing = pd.read_csv("All_Months_Listing.csv")

# Sold dataset — key off CloseDate
df_sold['year_month'] = pd.to_datetime(df_sold['CloseDate']).dt.to_period('M')

# Listings dataset — key off ListingContractDate
df_listing['year_month'] = pd.to_datetime(df_listing['ListingContractDate']).dt.to_period('M')

# Step 4 – Merge
sold_with_rates = df_sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = df_listing.merge(mortgage_monthly, on='year_month', how='left')
sold_with_rates.to_csv("Sold_With_Rates.csv", index=False)
listings_with_rates.to_csv("Listing_With_Rates.csv", index=False)

# Step 5 – Validate the merge
# Check for any unmatched rows (rate should not be null)
print("Nunber of null rows (sold): " + str(sold_with_rates['rate_30yr_fixed'].isnull().sum()))
print("Nunber of null rows (listing): " + str(listings_with_rates['rate_30yr_fixed'].isnull().sum()))
'''
None missing
'''

print(
    sold_with_rates[
        ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
    ].head()
)

'''
Sold Rates
    CloseDate year_month  ClosePrice  rate_30yr_fixed
0  2024-01-26    2024-01    240000.0           6.6425
1  2024-01-05    2024-01    815000.0           6.6425
2  2024-01-05    2024-01    810000.0           6.6425
3  2024-01-02    2024-01   2100000.0           6.6425
4  2024-01-22    2024-01   1950000.0           6.6425
'''
