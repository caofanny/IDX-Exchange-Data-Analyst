import pandas as pd

# ---------------------------------------------------------------
# Converting date fields to datetime format 
# ---------------------------------------------------------------
df_listing = pd.read_csv("All_Months_Listing.csv", low_memory=False)
df_sold = pd.read_csv("All_Months_Sold.csv", low_memory=False)

dateChanges = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]

for date in dateChanges:
    df_listing[date] = pd.to_datetime(df_listing[date], format="%Y-%m-%d")
    df_sold[date] = pd.to_datetime(df_sold[date], format="%Y-%m-%d", errors="coerce")

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
    'CoListAgentFirstName', 'CoListAgentLastName',
    'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName',
    'CoBuyerAgentFirstName', 'BuyerAgentAOR',
    'ListOfficeName', 'BuyerOfficeName', 'CoListOfficeName', 'BuyerOfficeAOR',
    'BuyerAgencyCompensation', 'BuyerAgencyCompensationType',
    'OriginatingSystemName', 'OriginatingSystemSubName', 'StreetNumberNumeric',
]

duplicates_sold = [col for col in df_sold.columns if col.endswith(".1")]
duplicates_listing = [col for col in df_listing.columns if col.endswith(".1")]

print(duplicates_sold)
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

print(df_sold_cleaned.columns)
# ---------------------------------------------------------------
# Ensure numeric fields are properly typed
# ---------------------------------------------------------------
numeric_fields_sold = ["OriginalListPrice", "ClosePrice", "Latitude", "Longitude", "ListPrice", "LivingArea",
                        "ListPrice", "DaysOnMarket", "AssociationFeeFrequency", "ParkingTotal", "LotSizeAcres", 
                        "YearBuilt", "BathroomsTotalInteger", "BedroomsTotal", "Stories", "LotSizeAcres", 
                        "LotSizeArea", "MainLevelBedrooms", "GarageSpaces", "AssociationFee", "LotSizeSquareFeet"]

numeric_fields_listing = ["OriginalListPrice", "ClosePrice", "Latitude", "Longitude", 
                        "LivingArea", "ListPrice", "DaysOnMarket", "AssociationFeeFrequency",
                        "ParkingTotal", "LotSizeAcres", "YearBuilt", "BathroomsTotalInteger",
                        "BedroomsTotal", "Stories", "LotSizeArea", "MainLevelBedrooms", "GarageSpaces",
                        "AssociationFee", "LotSizeSquareFeet"]

for col in numeric_fields_sold:
    df_sold[col] = pd.to_numeric(df_sold[col], errors="coerce")

for col in numeric_fields_listing:
    df_listing[col] = pd.to_numeric(df_listing[col], errors="coerce")

print("=====================================================================")
print("Sold Datatypes")
print(df_sold_cleaned.dtypes)
print("\nListing Datatypes")
print(df_listing_cleaned.dtypes)

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
df_sold_cleaned["any_invalid"] = df_sold_cleaned[invalid_cols].any(axis=1)

print("=====================================================================")
print("Invalid value counts:" + "\n" + str(df_sold_cleaned[invalid_cols].sum()))