import pandas as pd

# the filtering logic applied
# Include a missing value report flagging any columns above 90% null
# Produce a numeric distribution summary (min, max, mean, median, percentiles) for ClosePrice, LivingArea, and DaysOnMarket
# Save the filtered dataset as a new CSV.

# df_listing = pd.read_csv("All_Months_Listing.csv", low_memory=False)
df_sold = pd.read_csv("All_Months_Sold.csv", low_memory=False)
df_sold_unfiltered = pd.read_csv("All_Months_Sold_Unfiltered.csv", low_memory=False)

# ---------------------------------------------------------------
# Dataset Understanding
# ---------------------------------------------------------------
print(df_sold.shape) # (480484, 84) row, col

print(df_sold.dtypes) # column data types (all stored as objects)
print(df_sold_unfiltered["PropertyType"].unique()) # unique property types
print()
'''
Residential, CommercialLease, Land, ResidentialLease, ManufacturedInPark,
ResidentialIncome, CommercialSale, BusinessOpportunity
'''

'''
High Missing Columns: Flooring, WaterfrontYN, BasementYN, CoListAgentLastName, FireplacesTotal, AssociationFeeFrequency,
ElementarySchool, BuilderName, SubdivisionName, TaxYear, BuildingAreaTotal, ElementarySchoolDistrict, CoBuyerAgentFirstName,
BelowGradeFinishedArea, BusinessType, CoveredSpaces, MiddleOrJuniorSchool, HighSchool, LotSizeDimensions, MainLevelBedrooms,
MiddleOrJuniorSchoolDistrict, BuyerAgentAOR, ListAgentAOR, OriginatingSystemName, OriginatingSystemSubName
'''

MARKET_ANALYSIS_FIELDS = [
    # Price
    'OriginalListPrice', 'ListPrice', 'ClosePrice', 'CloseDate', 'ContractStatusChangeDate', 'PurchaseContractDate', 
    'ListingContractDate', 'DaysOnMarket', 'AssociationFee', 'AssociationFeeFrequency', 'TaxAnnualAmount'

    # Location
    'Latitude', 'Longitude', 'UnparsedAddress', 'City', 'CountyOrParish', 'StateOrProvince', 'PostalCode', 
    'MLSAreaMajor', 'SubdivisionName',

    # Property type / core characteristics
    'PropertyType', 'PropertySubType', 'LivingArea', 'BuildingAreaTotal', 'AboveGradeFinishedArea', 'BelowGradeFinishedArea',
    'BedroomsTotal', 'BathroomsTotalInteger', 'MainLevelBedrooms', 'YearBuilt', 'NewConstructionYN', 'Stories', 'Levels',
    'LotSizeAcres', 'LotSizeSquareFeet', 'LotSizeArea', 'LotSizeDimensions',

    # Amenities / features that drive pricing
    'GarageSpaces', 'ParkingTotal', 'CoveredSpaces', 'AttachedGarageYN', 'FireplacesTotal', 'FireplaceYN', 'ViewYN', 
    'WaterfrontYN', 'PoolPrivateYN', 'BasementYN'
]

METADATA_FIELDS = [
    # ID
    'ListingKey', 'ListingKeyNumeric', 'ListingId', 'MlsStatus', 'OriginatingSystemName', 'OriginatingSystemSubName', 
    'StreetNumberNumeric',

    # Agent
    'ListAgentEmail', 'ListAgentFirstName', 'ListAgentLastName', 'ListAgentFullName', 'ListAgentAOR', 'CoListAgentFirstName',
    'CoListAgentLastName', 'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName', 'CoBuyerAgentFirstName', 
    'BuyerAgentAOR',

    # Office / brokerage
    'ListOfficeName', 'BuyerOfficeName', 'CoListOfficeName', 'BuyerOfficeAOR',

    # Compensation
    'BuyerAgencyCompensation', 'BuyerAgencyCompensationType',

    'Flooring', 'TaxYear', 'BuilderName', 'BusinessType', 'ElementarySchool', 'ElementarySchoolDistrict', 'MiddleOrJuniorSchool',
    'MiddleOrJuniorSchoolDistrict', 'HighSchool', 'HighSchoolDistrict', 'latfilled', 'lonfilled'
]

# ---------------------------------------------------------------
# Missing Value Analysis
# ---------------------------------------------------------------
missing_counts = df_sold.isnull().sum()
missing_pct = missing_counts/len(df_sold) * 100
df_missing = pd.DataFrame({
    "missing_count": missing_counts,
    "missing_pct": missing_pct.round(2)
}).sort_values("missing_pct", ascending=False)

df_missing.to_csv("Missing_Value_Report.csv")
print("Null Count Summary (Top 10 missing columns by %):")
print(df_missing.head(10))
print()
'''
Null Count Summary (Top 10 missing columns by %):
                              missing_count  missing_pct
TaxYear                              480484       100.00
FireplacesTotal                      480484       100.00
TaxAnnualAmount                      480484       100.00
AboveGradeFinishedArea               480484       100.00
ElementarySchoolDistrict             480484       100.00
BusinessType                         480484       100.00
CoveredSpaces                        480484       100.00
MiddleOrJuniorSchoolDistrict         480484       100.00
WaterfrontYN                         480183        99.94
BelowGradeFinishedArea               477574        99.39
'''

flagged_cols = df_missing[df_missing["missing_pct"] > 90]
print("Columns with > 90% values missing:")
print(flagged_cols)
print()

'''
Missing Values Report (90% values missing):
                              missing_count  missing_pct
TaxYear                              480484       100.00
FireplacesTotal                      480484       100.00
TaxAnnualAmount                      480484       100.00
AboveGradeFinishedArea               480484       100.00
ElementarySchoolDistrict             480484       100.00
BusinessType                         480484       100.00
CoveredSpaces                        480484       100.00
MiddleOrJuniorSchoolDistrict         480484       100.00
WaterfrontYN                         480183        99.94
BelowGradeFinishedArea               477574        99.39
BasementYN                           471059        98.04
BuilderName                          457096        95.13
LotSizeDimensions                    457035        95.12
BuildingAreaTotal                    446764        92.98
CoBuyerAgentFirstName                436277        90.80
'''

# ---------------------------------------------------------------
# Numeric Distribution Review
# ---------------------------------------------------------------
numeric_distribution_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]
percentiles = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]

distribution_summary = []
for field in numeric_distribution_fields:
    row = {
        "field": field,
        "min": df_sold[field].min(),
        "max": df_sold[field].max(),
        "mean": round(df_sold[field].mean(), 2),
        "median": df_sold[field].median(),
    }
    quantiles = df_sold[field].quantile(percentiles)
    for percentile, value in quantiles.items():
        row[percentile] = value

    distribution_summary.append(row)

df_distribution_summary = pd.DataFrame(distribution_summary)
print("Distribution Summary: ")
print(df_distribution_summary)
df_distribution_summary.to_csv("Numeric_Distribution_Summary.csv", index=False)
    
