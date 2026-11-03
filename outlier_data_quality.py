import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------------
# Extreme values in price, price per square footage, close to list ratio, or days on 
# market can distort market averages and trends.
# Implement a statistical method to identify and remove these records.
# Use percentiles alongside IQR to guide decisions.
# -----------------------------------------------------------------------------------

# Method: Interquartile Range (IQR): removes records that fall outside a defined statistical range

df_sold = pd.read_csv("Sold_Features.csv", low_memory=False)
df_listing = pd.read_csv("Listing_Features.csv", low_memory=False)

no_invalid_sold = pd.Series(False, index=df_sold.index) # series of all false

invalids_sold = {
    "ClosePrice": df_sold["invalid_price"],
    "DaysOnMarket": df_sold["invalid_dom"],
    "LivingArea": df_sold["invalid_living_area"],
    "PricePerSqFt": no_invalid_sold,
    "CloseToOriginalListRatio": no_invalid_sold,
}
invalids_listing = {
    "ListPrice": df_listing["ListPrice"] <= 0,
    "DaysOnMarket": df_listing["invalid_dom"],
    "LivingArea": df_listing["invalid_living_area"],
}

# method and multiplier per field, chosen from the percentile checks
methods_sold = {
    "ClosePrice": "log_iqr",
    "DaysOnMarket": "percentile",
    "LivingArea": "log_iqr",
    "PricePerSqFt": "log_iqr",
    "CloseToOriginalListRatio": "iqr",
}
methods_listing = {
    "ListPrice": "log_iqr",
    "DaysOnMarket": "percentile",
    "LivingArea": "log_iqr",
}

def get_bounds(valid, method):
    if method == "iqr":
        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)
        iqr = q3 - q1
        return (q1 - 1.5 * iqr), np.exp(q3 + 1.5 * iqr)

    if method == "log_iqr":
        logs = np.log(valid[valid > 0])
        q1 = logs.quantile(0.25)
        q3 = logs.quantile(0.75)
        iqr = q3 - q1
        # convert back from log scale so bounds are in dollars / sq ft
        return np.exp(q1 - 1.5 * iqr), np.exp(q3 + 1.5 * iqr)
 
    if method == "percentile":
        return valid.quantile(0.01), valid.quantile(0.99)
    
def flag_outliers_iqr(df, invalids, methods):
    df_new = df.copy()
    for column, invalid in invalids.items():
        # get bounds from valid values only
        valid = df_new.loc[~invalid, column].dropna()
        method = methods[column]
        lower, upper = get_bounds(valid, method)
 
        df_new[f"Outlier{column}"] = ((df_new[column] < lower) | (df_new[column] > upper)) & ~invalid
        print(f"{column} ({method}): bounds [{lower:,.2f}, {upper:,.2f}], "
              f"flagged {df_new[f'Outlier{column}'].sum():,} "
              f"({df_new[f'Outlier{column}'].mean():.1%})")
 
        p1, p5, p95, p99 = valid.quantile([0.01, 0.05, 0.95, 0.99])
        print(f"  lower bound {lower:,.2f} vs 1st pct {p1:,.2f}, 5th pct {p5:,.2f}")
        print(f"  upper bound {upper:,.2f} vs 95th pct {p95:,.2f}, 99th pct {p99:,.2f}")
    
    df_new["AnyOutlier"] = df_new[[f"Outlier{column}" for column in invalids]].any(axis=1)
    return df_new

def compare(df_before, df_after, fields):
    comparison = pd.DataFrame({
        "Before": [len(df_before)] + [df_before[f].median() for f in fields],
        "After": [len(df_after)] + [df_after[f].median() for f in fields],
    }, index=["Rows"] + [f"Median {f}" for f in fields])
    comparison["Change %"] = (comparison["After"] / comparison["Before"] - 1) * 100
    print(comparison.round(2).to_string())


print("Sold:")
df_sold_flagged = flag_outliers_iqr(df_sold, invalids_sold, methods_sold)
print("Listing:")
df_listing_flagged = flag_outliers_iqr(df_listing, invalids_listing, methods_listing)

any_invalid_sold = df_sold[["invalid_price", "invalid_dom", "invalid_living_area"]].any(axis=1)
any_invalid_listing = df_listing[["invalid_dom", "invalid_living_area"]].any(axis=1) | (df_listing["ListPrice"] <= 0)

df_sold_removed = df_sold_flagged[~any_invalid_sold & ~df_sold_flagged["AnyOutlier"]].copy() 
df_listing_removed = df_listing_flagged[~any_invalid_listing & ~df_listing_flagged["AnyOutlier"]].copy()    

df_sold_flagged.to_csv("Sold_Flagged.csv", index=False, encoding="utf-8")
df_sold_removed.to_csv("Sold_Filtered_Removed.csv", index=False, encoding="utf-8")
df_listing_flagged.to_csv("Listing_Flagged.csv", index=False, encoding="utf-8")
df_listing_removed.to_csv("Listing_Filtered_Removed.csv", index=False, encoding="utf-8")

print("Sold comparison:")
compare(df_sold_flagged, df_sold_removed,["ClosePrice", "LivingArea", "DaysOnMarket", "PricePerSqFt", "CloseToOriginalListRatio"])
print("Listing comparison:")
compare(df_listing_flagged, df_listing_removed, ["ListPrice", "LivingArea", "DaysOnMarket"])

'''
Sold:
ClosePrice (log_iqr): bounds [169,143.22, 4,419,331.85], flagged 11,526 (2.4%)
  lower bound 169,143.22 vs 1st pct 200,000.00, 5th pct 339,000.00
  upper bound 4,419,331.85 vs 95th pct 2,850,000.00, 99th pct 5,600,000.00
DaysOnMarket (percentile): bounds [0.00, 234.00], flagged 4,796 (1.0%)
  lower bound 0.00 vs 1st pct 0.00, 5th pct 1.00
  upper bound 234.00 vs 95th pct 132.00, 99th pct 234.00
LivingArea (log_iqr): bounds [525.65, 5,295.85], flagged 6,853 (1.4%)
  lower bound 525.65 vs 1st pct 610.00, 5th pct 840.00
  upper bound 5,295.85 vs 95th pct 3,568.00, 99th pct 5,298.58
PricePerSqFt (log_iqr): bounds [130.83, 2,054.57], flagged 5,800 (1.2%)
  lower bound 130.83 vs 1st pct 160.29, 5th pct 225.76
  upper bound 2,054.57 vs 95th pct 1,216.25, 99th pct 1,892.50
CloseToOriginalListRatio (iqr): bounds [0.85, 3.06], flagged 23,119 (4.8%)
  lower bound 0.85 vs 1st pct 0.75, 5th pct 0.86
  upper bound 3.06 vs 95th pct 1.11, 99th pct 1.29

Listing:
ListPrice (log_iqr): bounds [159,002.03, 5,011,147.30], flagged 17,184 (2.7%)
  lower bound 159,002.03 vs 1st pct 210,000.00, 5th pct 344,900.00
  upper bound 5,011,147.30 vs 95th pct 3,399,000.00, 99th pct 8,095,570.00
DaysOnMarket (percentile): bounds [0.00, 134.00], flagged 6,266 (1.0%)
  lower bound 0.00 vs 1st pct 0.00, 5th pct 0.00
  upper bound 134.00 vs 95th pct 78.00, 99th pct 134.00
LivingArea (log_iqr): bounds [498.82, 5,754.37], flagged 10,904 (1.7%)
  lower bound 498.82 vs 1st pct 593.00, 5th pct 821.00
  upper bound 5,754.37 vs 95th pct 3,859.00, 99th pct 6,272.00

Sold comparison:
                                    Before      After  Change %
Rows                             480484.00  447618.00     -6.84
Median ClosePrice                825000.00  810000.00     -1.82
Median LivingArea                  1647.00    1636.00     -0.67
Median DaysOnMarket                  19.00      18.00     -5.26
Median PricePerSqFt                 536.42     529.95     -1.21
Median CloseToOriginalListRatio       0.99       1.00      0.16

Listing comparison:
                       Before     After  Change %
Rows                 630083.0  602074.0     -4.45
Median ListPrice     840000.0  827851.0     -1.45
Median LivingArea      1670.0    1652.0     -1.08
Median DaysOnMarket      11.0      11.0      0.00
'''

'''
Log-IQR was used for right-skewed fields, where IQR gave negative lower bounds and flagged legitimate high-end sales.
Percentages was used for fields with 0.
'''