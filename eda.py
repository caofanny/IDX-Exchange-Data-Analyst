import pandas as pd;

df_listing = pd.read_csv("All_Months_Listing.csv", low_memory=False)
df_sold = pd.read_csv("All_Months_Sold.csv", low_memory=False)
df_sold_unfiltered = pd.read_csv("All_Months_Sold_Unfiltered.csv", low_memory=False)

# ---------------------------------------------------------------
# Q1: Residential vs. other property type share
# ---------------------------------------------------------------
sold_property_types = df_sold_unfiltered["PropertyType"].value_counts(normalize=True)*100
print(str(sold_property_types.round(2)))
print()
'''
Residential            67.26
ResidentialLease       23.00
Land                    3.18
ManufacturedInPark      2.68
ResidentialIncome       2.68
CommercialSale          0.61
CommercialLease         0.52
BusinessOpportunity     0.06
'''

# ---------------------------------------------------------------
# Q2: Median & average close prices
# ---------------------------------------------------------------
median_closing_price_listing = df_listing["ClosePrice"].median()
avg_closing_price_listing = df_listing["ClosePrice"].mean()

median_closing_price_sold = df_sold["ClosePrice"].median()
avg_closing_price_sold = df_sold["ClosePrice"].mean()

print("listing median: ", median_closing_price_listing)
print("listing avg: ", avg_closing_price_listing.round(2))
print("sold median: ", median_closing_price_sold.round(2))
print("sold avg: ", avg_closing_price_sold.round(2))
print()
'''
listing median:  855,000.0
listing avg:  1,201,728.67
sold median:  825,000.0
sold avg:  1,189,603.10
'''

# ---------------------------------------------------------------
# Q3: What does the Days on Market distribution look like?
# ---------------------------------------------------------------
min_dom_sold = df_sold["DaysOnMarket"].min()
max_dom_sold = df_sold["DaysOnMarket"].max()
quartiles_sold = df_sold["DaysOnMarket"].quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])

min_dom_listing = df_listing["DaysOnMarket"].min()
max_dom_listing = df_listing["DaysOnMarket"].max()
quartiles_listing = df_listing["DaysOnMarket"].quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])

print("Sold Lowest: " + str(min_dom_sold), "Highest: " + str(max_dom_sold))
print("Sold Quartiles", str(quartiles_sold))

'''
Sold Lowest: -288 
Sold Highest: 12430
Sold Quartiles: 
0.10      4.0
0.25      8.0
0.50     19.0
0.75     48.0
0.90     94.0
0.95    132.0
0.99    234.0
'''

print("Listing Lowest: " + str(min_dom_listing), "Highest: " + str(max_dom_listing))
print("Listing Quartiles", str(quartiles_listing))

'''
Listing Lowest: -58 
Highest: 1155
Listing Quartiles: 
0.10      1.0
0.25      5.0
0.50     11.0
0.75     24.0
0.90     50.0
0.95     78.0
0.99    134.0
'''

'''
Sold
50% of the listings are on the market for 19 days or less before being sold. 95% are on the market for 132 days.
There is an outlier of 1155 days and only 1% of the listings get sold after 234 days. The minimum is -288 days, which
means there might be some invalid data, and the high is 12430 days.
'''

# ---------------------------------------------------------------
# Q4: Percentage of homes sold above vs. below list price
# ---------------------------------------------------------------
total = len(df_sold)
sold_above = df_sold[df_sold["ClosePrice"] > df_sold["ListPrice"]]
sold_below = df_sold[df_sold["ClosePrice"] < df_sold["ListPrice"]]
print("Percentage sold above: " + str((len(sold_above)/total).__round__(2)))
print("Percentage sold below: " + str((len(sold_below)/total).__round__(2)))
print()

'''
Percentage sold above: 0.4
Percentage sold below: 0.43
'''

# ---------------------------------------------------------------
# Q5: Date consistency issues (e.g., close date before listing date)?
# ---------------------------------------------------------------
listing_after_purchase = (df_sold['ListingContractDate'] > df_sold['PurchaseContractDate']).sum()
purchase_after_close = (df_sold['PurchaseContractDate'] > df_sold['CloseDate']).sum()
listing_after_close = (df_sold['ListingContractDate'] > df_sold['CloseDate']).sum()
print("Number of listing after purchase date: " + str(listing_after_purchase))
print("Number of purchase after close date: " + str(purchase_after_close))
print("Number of listing after close date: " + str(listing_after_close))
print()

'''
Number of listing after purchase date: 311
Number of purchase after close date: 243
Number of listing after close date: 74
'''

# ---------------------------------------------------------------
# Q6: Which counties have the highest median prices?
# ---------------------------------------------------------------
counties_sold = df_sold.groupby("CountyOrParish")["ClosePrice"].median().sort_values(ascending=False)
print(counties_sold.head(10))
print()

'''
Highest Median Prices (Sold)
Del Norte        2,485,000.0
San Mateo        1,700,000.0
Santa Clara      1,592,000.0
San Francisco    1,200,000.0
Santa Cruz       1,195,000.0
Orange           1,185,000.0
Marin            1,170,000.0
Alameda          1,135,000.0
Alpine           1,100,000.0
Other County     1,100,000.0
'''

counties_listing = df_listing.groupby("CountyOrParish")["ClosePrice"].median().sort_values(ascending=False)
print(counties_listing.head(10))
print()

'''
Highest Median Prices (Listing)
CountyOrParish
San Mateo        1,750,000.0
Santa Clara      1,635,000.0
Marin            1,293,500.0
San Francisco    1,256,000.0
Santa Cruz       1.215,000.0
Orange           1.180,000.0
Alameda          1,175,000.0
Los Angeles       925,000.0
Monterey          915,000.0
San Diego         903,000.0
'''