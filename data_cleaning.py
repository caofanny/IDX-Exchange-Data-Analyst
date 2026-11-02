import pandas as pd

# ---------------------------------------------------------------
# Converting date fields to datetime format 
# ---------------------------------------------------------------
df_listing = pd.read_csv("Listing_With_Rates.csv", low_memory=False)
df_sold = pd.read_csv("Sold_With_Rates.csv", low_memory=False)

dateChanges = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]

for date in dateChanges:
    df_listing[date] = pd.to_datetime(df_listing[date], format="%Y-%m-%d")
    df_sold[date] = pd.to_datetime(df_sold[date], format="%Y-%m-%d", errors="coerce")

# ---------------------------------------------------------------
# Ensure numeric fields are properly typed
# ---------------------------------------------------------------
numeric_fields = ["OriginalListPrice", "ClosePrice", "Latitude", "Longitude", "ListPrice",
                  "LivingArea", "DaysOnMarket", "ParkingTotal", "LotSizeAcres", "YearBuilt",
                  "BathroomsTotalInteger", "BedroomsTotal", "Stories", "LotSizeArea",
                  "MainLevelBedrooms", "GarageSpaces", "AssociationFee", "LotSizeSquareFeet"]


for col in numeric_fields:
    if col in df_sold.columns:
        df_sold[col] = pd.to_numeric(df_sold[col], errors="coerce")
    if col in df_listing.columns:
        df_listing[col] = pd.to_numeric(df_listing[col], errors="coerce")


print("=====================================================================")
print("Sold Datatypes")
print(df_sold.dtypes)
print("\nListing Datatypes")
print(df_listing.dtypes)

# ------------------------------------------------------------------
# Remove unnecessary, redundant, duplicate and high missing columns
# ------------------------------------------------------------------
missing_columns_sold = pd.read_csv("Missing_Value_Report_Sold.csv", index_col=0)
missing_columns_listing = pd.read_csv("Missing_Value_Report_Listing.csv", index_col=0)

# Columns flagged >90% missing 
high_missing_sold = missing_columns_sold[missing_columns_sold["missing_pct"] > 90].index.to_list()
high_missing_listing = missing_columns_listing[missing_columns_listing["missing_pct"] > 90].index.to_list()

# Metadata fields not needed for analysis
cols_to_drop_metadata = [
    'ListingKey', 'ListingKeyNumeric', 'ListingId', 'MlsStatus', 'ListAgentEmail',
    'ListAgentFirstName', 'ListAgentLastName', 'ListAgentFullName', 'ListAgentAOR',
    'CoListAgentFirstName', 'CoListAgentLastName','BuyerAgentMlsId', 'BuyerAgentFirstName', 
    'BuyerAgentLastName', 'CoBuyerAgentFirstName', 'BuyerAgentAOR', 'CoListOfficeName', 
    'BuyerOfficeAOR', 'BuyerAgencyCompensation', 'BuyerAgencyCompensationType',
    'OriginatingSystemName', 'OriginatingSystemSubName', 'StreetNumberNumeric',
]

duplicates_sold = [col for col in df_sold.columns if col.endswith(".1")]
duplicates_listing = [col for col in df_listing.columns if col.endswith(".1")]

# Columns that should be dropped
cols_to_drop_sold = list(set(high_missing_sold + cols_to_drop_metadata + duplicates_sold))
cols_to_drop_listing = list(set(high_missing_listing + cols_to_drop_metadata + duplicates_listing))

# Dropping the columns if the columns in the list are found in the dataframe
df_sold_cleaned = df_sold.drop(columns=[col for col in cols_to_drop_sold if col in df_sold.columns])
df_listing_cleaned = df_listing.drop(columns=[col for col in cols_to_drop_listing if col in df_listing.columns])

print("=====================================================================")
print("Sold columns BEFORE dropping: " + str(len(df_sold.columns)))
print("Sold columns AFTER dropping: " + str(len(df_sold_cleaned.columns)))
print("Sold columns dropped #: " + str(len(cols_to_drop_sold)))
print("\nListing columns BEFORE dropping: " + str(len(df_listing.columns)))
print("Listing columns AFTER dropping: " + str(len(df_listing_cleaned.columns)))
print("Listing columns dropped #: " + str(len(cols_to_drop_listing)))

'''
Sold columns BEFORE dropping: 86
Sold columns AFTER dropping: 49
Sold columns dropped #: 37

Listing columns BEFORE dropping: 86
Listing columns AFTER dropping: 44
Listing columns dropped #: 46
'''

# ---------------------------------------------------------------
# Flag invalid numeric values
# ---------------------------------------------------------------
df_sold_cleaned["invalid_price"] = df_sold_cleaned["ClosePrice"] <= 0
df_sold_cleaned["invalid_living_area"] = df_sold_cleaned["LivingArea"] <= 0
df_sold_cleaned["invalid_dom"] = df_sold_cleaned["DaysOnMarket"] < 0
df_sold_cleaned["invalid_bedrooms"] = df_sold_cleaned["BedroomsTotal"] < 0
df_sold_cleaned["invalid_bathrooms"] = df_sold_cleaned["BathroomsTotalInteger"] < 0

df_listing_cleaned["invalid_price"] = df_listing_cleaned["ClosePrice"] <= 0
df_listing_cleaned["invalid_living_area"] = df_listing_cleaned["LivingArea"] <= 0
df_listing_cleaned["invalid_dom"] = df_listing_cleaned["DaysOnMarket"] < 0
df_listing_cleaned["invalid_bedrooms"] = df_listing_cleaned["BedroomsTotal"] < 0
df_listing_cleaned["invalid_bathrooms"] = df_listing_cleaned["BathroomsTotalInteger"] < 0

invalid_cols = ["invalid_price", "invalid_living_area", "invalid_dom", "invalid_bedrooms", "invalid_bathrooms"]
df_sold_cleaned["any_invalid_numerical_values"] = df_sold_cleaned[invalid_cols].any(axis=1)
df_listing_cleaned["any_invalid_numerical_values"] = df_listing_cleaned[invalid_cols].any(axis=1)
invalid_cols.append("any_invalid_numerical_values")

print("=====================================================================")
print("Invalid sold value counts:" + "\n" + str(df_sold_cleaned[invalid_cols].sum()))
print("Invalid listing value counts:" + "\n" + str(df_listing_cleaned[invalid_cols].sum()))

'''
Invalid sold value counts:
invalid_price                     1
invalid_living_area             172
invalid_dom                      54
invalid_bedrooms                  0
invalid_bathrooms                 0
any_invalid_numerical_values    227

Invalid listing value counts:
invalid_price                     0
invalid_living_area             404
invalid_dom                      31
invalid_bedrooms                  0
invalid_bathrooms                 0
any_invalid_numerical_values    435
'''

# ---------------------------------------------------------------
# Date Consistency Checks
# ---------------------------------------------------------------
df_sold_cleaned["listing_after_close_flag"] = df_sold_cleaned["ListingContractDate"] > df_sold_cleaned["CloseDate"]
df_sold_cleaned["purchase_after_close_flag"] = df_sold_cleaned["PurchaseContractDate"] > df_sold_cleaned["CloseDate"]
df_sold_cleaned["listing_after_purchase_flag"] = df_sold_cleaned["ListingContractDate"] > df_sold_cleaned["PurchaseContractDate"]
df_sold_cleaned["negative_timeline_flag"] = df_sold_cleaned[
    ["listing_after_close_flag", "purchase_after_close_flag", "listing_after_purchase_flag"]].any(axis=1)

df_listing_cleaned["listing_after_close_flag"] = df_listing_cleaned["ListingContractDate"] > df_listing_cleaned["CloseDate"]
df_listing_cleaned["purchase_after_close_flag"] = df_listing_cleaned["PurchaseContractDate"] > df_listing_cleaned["CloseDate"]
df_listing_cleaned["listing_after_purchase_flag"] = df_listing_cleaned["ListingContractDate"] > df_listing_cleaned["PurchaseContractDate"]
df_listing_cleaned["negative_timeline_flag"] = df_listing_cleaned[
    ["listing_after_close_flag", "purchase_after_close_flag", "listing_after_purchase_flag"]].any(axis=1)

print("=====================================================================")
print("Sold:")
print("Listing after purchase date #: " + str((df_sold_cleaned["listing_after_purchase_flag"] == 1).sum()))
print("Purchase after close date #: " + str((df_sold_cleaned["purchase_after_close_flag"] == 1).sum()))
print("Listing after close date #: " + str((df_sold_cleaned["listing_after_close_flag"] == 1).sum()))
print("Flagged rows #: " + str((df_sold_cleaned["negative_timeline_flag"] == 1).sum()))

print("Listing:")
print("Listing after purchase date #: " + str((df_listing_cleaned["listing_after_purchase_flag"] == 1).sum()))
print("Purchase after close date #: " + str((df_listing_cleaned["purchase_after_close_flag"] == 1).sum()))
print("Listing after close date #: " + str((df_listing_cleaned["listing_after_close_flag"] == 1).sum()))
print("Flagged rows #: " + str((df_listing_cleaned["negative_timeline_flag"] == 1).sum()))

'''
Sold:
Listing after purchase date #: 311
Purchase after close date #: 243
Listing after close date #: 74
Flagged rows #: 554

Listing:
Listing after purchase date #: 314
Purchase after close date #: 265
Listing after close date #: 89
Flagged rows #: 578
'''

# ---------------------------------------------------------------
# Geographic Data Checks
# ---------------------------------------------------------------
df_sold_cleaned["missing_coordinate_flag"] = df_sold_cleaned["Longitude"].isna() | df_sold_cleaned["Latitude"].isna()
df_sold_cleaned["zero_coordinate_flag"] = (df_sold_cleaned["Longitude"] == 0) | (df_sold_cleaned["Latitude"] == 0)
df_sold_cleaned["negative_longitude_flag"] = df_sold_cleaned["Longitude"] > 0

df_listing_cleaned["missing_coordinate_flag"] = df_listing_cleaned["Longitude"].isna() | df_listing_cleaned["Latitude"].isna()
df_listing_cleaned["zero_coordinate_flag"] = (df_listing_cleaned["Longitude"] == 0) | (df_listing_cleaned["Latitude"] == 0)
df_listing_cleaned["negative_longitude_flag"] = df_listing_cleaned["Longitude"] > 0

# CA Lat: 32° to 42° | CA Long: –114° to –124°
is_ca = df_sold_cleaned["Latitude"].between(32, 42) & df_sold_cleaned["Longitude"].between(-124, -114)
is_valid = (~df_sold_cleaned["missing_coordinate_flag"] & 
            ~df_sold_cleaned["zero_coordinate_flag"] & 
            ~df_sold_cleaned["negative_longitude_flag"])

df_sold_cleaned["out_of_state_coordinate_flag"] = is_valid & ~is_ca

is_ca = df_listing_cleaned["Latitude"].between(32, 42) & df_listing_cleaned["Longitude"].between(-124, -114)
is_valid = (~df_listing_cleaned["missing_coordinate_flag"] & 
            ~df_listing_cleaned["zero_coordinate_flag"] & 
            ~df_listing_cleaned["negative_longitude_flag"])

df_listing_cleaned["out_of_state_coordinate_flag"] = is_valid & ~is_ca

print("=====================================================================")
print("Sold:")
print("Missing coordinate #: " + str((df_sold_cleaned["missing_coordinate_flag"] == 1).sum()))
print("Zero coordinate #: " + str((df_sold_cleaned["zero_coordinate_flag"] == 1).sum()))
print("Negative longitude #: " + str((df_sold_cleaned["negative_longitude_flag"] == 1).sum()))
print("Out of state coordinate #: " + str((df_sold_cleaned["out_of_state_coordinate_flag"] == 1).sum()))

print("Listing:")
print("Missing coordinate #: " + str((df_listing_cleaned["missing_coordinate_flag"] == 1).sum()))
print("Zero coordinate #: " + str((df_listing_cleaned["zero_coordinate_flag"] == 1).sum()))
print("Negative longitude #: " + str((df_listing_cleaned["negative_longitude_flag"] == 1).sum()))
print("Out of state coordinate #: " + str((df_listing_cleaned["out_of_state_coordinate_flag"] == 1).sum()))

'''
Sold:
Missing coordinate #: 4679
Zero coordinate #: 42
Negative longitude #: 35
Out of state coordinate #: 46

Listing:
Missing coordinate #: 81092
Zero coordinate #: 82
Negative longitude #: 93
Out of state coordinate #: 209
'''

df_sold_cleaned.to_csv("Sold_Cleaned.csv", index=False, encoding="utf-8")
df_listing_cleaned.to_csv("Listing_Cleaned.csv", index=False, encoding="utf-8")