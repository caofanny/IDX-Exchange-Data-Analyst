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

# ---------------------------------------------------------------
# Remove unnecessary or redundant columns
# ---------------------------------------------------------------
missing_columns_sold = pd.read_csv("Missing_Value_Report_Sold.csv", index_col=0)
missing_columns_listing = pd.read_csv("Missing_Value_Report_Listing.csv", index_col=0)
print(missing_columns_sold[missing_columns_sold["missing_pct"] > 90])

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

cols_to_drop_sold = list(set(high_missing_sold + cols_to_drop_metadata))
cols_to_drop_listing = list(set(high_missing_listing + cols_to_drop_metadata))

df_sold = df_sold.drop(columns=[col for col in cols_to_drop_sold if col in df_sold.columns])
df_listing = df_listing.drop(columns=[col for col in cols_to_drop_listing if col in df_listing.columns])

# ---------------------------------------------------------------
# Ensure numeric fields are properly typed
# ---------------------------------------------------------------
numeric_fields = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
                   "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
                   "DaysOnMarket", "YearBuilt"]

for col in numeric_fields:
    df_sold[col] = pd.to_numeric(df_sold[col], errors="coerce")
    df_listing[col] = pd.to_numeric(df_listing[col], errors="coerce")

# ---------------------------------------------------------------
# Ensure numeric fields are properly typed
# ---------------------------------------------------------------


