import pandas as pd
import geopandas as gpd

def safe_divide(numerator, denominator):
    return numerator / denominator.where(denominator > 0)

df_sold = pd.read_csv("Sold_Cleaned.csv", low_memory=False)
df_listing = pd.read_csv("Listing_Cleaned.csv", low_memory=False)

date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]

for date in date_cols:
    df_sold[date] = pd.to_datetime(df_sold[date], errors="coerce", format="%Y-%m-%d")
    df_listing[date] = pd.to_datetime(df_listing[date], errors="coerce", format="%Y-%m-%d")

# ---------------------------------------------------------------
# Creating Key Metrics 
# ---------------------------------------------------------------
# Price Ratio: measures negotiation strength
df_sold["PriceRatio"] = safe_divide(df_sold["ClosePrice"],  df_sold["ListPrice"])
df_listing["PriceRatio"] = safe_divide(df_listing["ClosePrice"], df_listing["ListPrice"])

# Price Per Sq Ft: normalizes price across sizes
df_sold["PricePerSqFt"] = safe_divide(df_sold["ClosePrice"], df_sold["LivingArea"])
df_listing["PricePerSqFt"] = safe_divide(df_listing["ClosePrice"], df_listing["LivingArea"])

# Days on Market:time-to-sell indicator
df_sold["DaysOnMarket"] = df_sold["DaysOnMarket"].where(~df_sold["invalid_dom"])
df_listing["DaysOnMarket"] = df_listing["DaysOnMarket"].where(~df_listing["invalid_dom"])

# Year / Month / YrMo: Enables time-series analysis
df_sold["Year"] = df_sold["CloseDate"].dt.year
df_sold["Month"] = df_sold["CloseDate"].dt.month
df_sold["YrMo"] = df_sold["CloseDate"].dt.to_period("M").astype(str)

df_listing["Year"] = df_listing["CloseDate"].dt.year
df_listing["Month"] = df_listing["CloseDate"].dt.month
df_listing["YrMo"] = pd.to_datetime(df_listing['CloseDate']).dt.to_period('M')

# Close to Original List Ratio: captures full price reduction history
df_sold["CloseToOriginalListRatio"] = safe_divide(df_sold["ClosePrice"], df_sold["OriginalListPrice"])
df_listing["CloseToOriginalListRatio"] = safe_divide(df_listing["ClosePrice"], df_listing["OriginalListPrice"])

# Listing to Contract Days: measures time from listing to accepted offer
df_sold["ListingToContractDays"] = (df_sold["PurchaseContractDate"] - df_sold["ListingContractDate"]).dt.days
df_sold["ListingToContractDays"] = df_sold["ListingToContractDays"].where(~df_sold["listing_after_purchase_flag"])

# Contract to Close Days: escrow and closing period duration
df_sold["ContractToCloseDays"] = (df_sold["CloseDate"] - df_sold["PurchaseContractDate"]).dt.days
df_sold["ContractToCloseDays"] = df_sold["ContractToCloseDays"].where(~df_sold["purchase_after_close_flag"])

# ---------------------------------------------------------------
# Adding School Districts
# ---------------------------------------------------------------
districts = gpd.read_file("school_districts.zip")

valid_coords = ~(
    df_sold["missing_coordinate_flag"]
    | df_sold["zero_coordinate_flag"]
    | df_sold["negative_longitude_flag"]
    | df_sold["out_of_state_coordinate_flag"]
)

DISTRICT_NAME = "DistrictNa"
DISTRICT_TYPE = "DistrictTy"
districts = districts.to_crs("EPSG:4326")

points = gpd.GeoDataFrame(
    index=df_sold.index[valid_coords],
    geometry=gpd.points_from_xy(
        df_sold.loc[valid_coords, "Longitude"],   # x = longitude
        df_sold.loc[valid_coords, "Latitude"],    # y = latitude
    ),
    crs="EPSG:4326",
)

joined = gpd.sjoin(points, districts[[DISTRICT_NAME, DISTRICT_TYPE, "geometry"]],
                   how="left", predicate="within")

# drop na and dupes
district_cols = (
    joined.reset_index()
    .dropna(subset=[DISTRICT_TYPE])
    .drop_duplicates(subset=["index", DISTRICT_TYPE])
    .pivot(index="index", columns=DISTRICT_TYPE, values=DISTRICT_NAME)
    .add_prefix("SchoolDistrict_")
)

district_cols.columns = [col.replace(" ", "") for col in district_cols.columns]
df_sold = df_sold.join(district_cols)

df_sold["SchoolDistrict"] = (
    df_sold["SchoolDistrict_Unified"]
    .fillna(df_sold["SchoolDistrict_High"])
    .fillna(df_sold["SchoolDistrict_Elementary"])
)

df_sold.to_csv("Sold_Features.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------
# Segment Analysis
# ---------------------------------------------------------------
def segment_summary(df, group_cols, min_sales=1):
    summary = (
        df.groupby(group_cols)
        .agg(
            Sales=("ClosePrice", "size"),
            MedianClosePrice=("ClosePrice", "median"),
            MedianPricePerSqFt=("PricePerSqFt", "median"),
            MedianPriceRatio=("PriceRatio", "median"),
            MedianCloseToOrigRatio=("CloseToOriginalListRatio", "median"),
            MedianDaysOnMarket=("DaysOnMarket", "median"),
            MedianListToContract=("ListingToContractDays", "median"),
            MedianContractToClose=("ContractToCloseDays", "median"),
        )
        .reset_index()
    )
    return summary[summary["Sales"] >= min_sales].sort_values("Sales", ascending=False)

segments = {
    "seg_property_type": (["PropertyType", "PropertySubType"], 1),
    "seg_county_area": (["CountyOrParish", "MLSAreaMajor"], 1),
    "seg_list_office": (["ListOfficeName"], 10),
    "seg_buyer_office": (["BuyerOfficeName"], 10),
    "seg_school_district": (["SchoolDistrict"], 10),
}

for name, (cols, min_sales) in segments.items():
    result = segment_summary(df_sold, cols, min_sales)
    result.to_csv(f"{name}.csv", index=False, encoding="utf-8")
    print("=====================================================================")
    print(f"{name}: {len(result)} groups")
    print(result.head(10).round(2).to_string(index=False))

'''
seg_property_type: 20 groups
PropertyType       PropertySubType  Sales  MedianClosePrice  MedianPricePerSqFt  MedianPriceRatio  MedianCloseToOrigRatio  MedianDaysOnMarket  MedianListToContract  MedianContractToClose
 Residential SingleFamilyResidence 360024          897000.0              532.67              1.00                    1.00                17.0                  24.0                   29.0
 Residential           Condominium  78860          625000.0              562.41              1.00                    0.99                25.0                  30.0                   28.0
 Residential             Townhouse  28116          800000.0              559.06              1.00                    1.00                18.0                  22.0                   28.0
 Residential    ManufacturedOnLand   6204          320000.0              225.36              0.99                    0.97                30.0                  39.0                   33.0
 Residential                Duplex   2694          910000.0              543.48              1.00                    0.98                21.0                  31.0                   32.0
 Residential      StockCooperative   1880          360000.0              396.71              0.99                    0.98                21.0                  32.0                   46.0
 Residential                 Cabin    559          250000.0              298.15              0.97                    0.92                45.0                  54.0                   30.0
 Residential               Triplex    414         1105000.0              466.97              0.98                    0.97                30.0                  46.5                   35.0
 Residential              MixedUse    241          670000.0              426.66              0.97                    0.93                53.0                  67.0                   32.0
 Residential            Quadruplex    179         1275000.0              374.32              0.97                    0.95                34.0                  43.0                   36.0

seg_county_area: 1248 groups
CountyOrParish                         MLSAreaMajor  Sales  MedianClosePrice  MedianPricePerSqFt  MedianPriceRatio  MedianCloseToOrigRatio  MedianDaysOnMarket  MedianListToContract  MedianContractToClose
     Riverside   SRCAR - Southwest Riverside County  23429          589000.0              294.12              1.00                    1.00                23.0                  32.0                   31.0
   Santa Clara                    699 - Not Defined  19049         1600000.0              970.84              1.02                    1.02                10.0                  10.0                   24.0
     San Mateo                    699 - Not Defined   7710         1730000.0             1061.31              1.01                    1.01                12.0                  12.0                   23.0
     Riverside                      252 - Riverside   6097          660000.0              378.67              1.00                    1.00                20.0                  28.0                   31.0
      Monterey                    699 - Not Defined   4438          915000.0              593.86              0.99                    0.98                19.0                  21.0                   28.0
     Riverside                         248 - Corona   3850          757650.0              397.00              1.00                    0.99                21.0                  30.0                   30.0
   Los Angeles                      LAC - Lancaster   3566          475000.0              270.53              1.00                    1.00                25.0                  30.0                   34.0
San Bernardino                    VIC - Victorville   3407          438000.0              238.59              1.00                    1.00                25.0                  32.0                   34.0
     Riverside 263 - Banning/Beaumont/Cherry Valley   3384          499000.0              260.00              1.00                    0.99                30.0                  37.0                   34.0
San Bernardino                 274 - San Bernardino   3336          500000.0              354.15              1.00                    1.00                20.0                  28.0                   33.0

seg_list_office: 4658 groups
                                       ListOfficeName  Sales  MedianClosePrice  MedianPricePerSqFt  MedianPriceRatio  MedianCloseToOrigRatio  MedianDaysOnMarket  MedianListToContract  MedianContractToClose
                                              Compass  34029         1350000.0              754.55              1.00                    1.00                14.0                  17.0                   25.0
                               Coldwell Banker Realty  21592         1200000.0              692.31              1.00                    1.00                16.0                  22.0                   25.0
                               Keller Williams Realty   9414          875000.0              540.31              1.00                    1.00                15.0                  22.0                   28.0
                               First Team Real Estate   6726          960000.0              608.89              1.00                    1.00                13.0                  27.0                   29.0
Berkshire Hathaway HomeServices California Properties   6106          958300.0              600.68              0.99                    0.98                23.0                  29.0                   28.0
                                          Real Broker   5603          850000.0              558.70              1.00                    1.00                15.0                  24.0                   27.0
                         eXp Realty of California Inc   5586          790000.0              530.43              1.00                    1.00                19.0                  26.0                   29.0
                          Intero Real Estate Services   5060         1370000.0              844.85              1.01                    1.01                12.0                  12.0                   25.0
                                         Equity Union   4318          851500.0              477.82              0.99                    0.98                28.0                  33.0                   27.0
                       eXp Realty of California, Inc.   4169          760000.0              490.00              1.00                    1.00                13.0                  21.0                   27.0

seg_buyer_office: 4547 groups
                                      BuyerOfficeName  Sales  MedianClosePrice  MedianPricePerSqFt  MedianPriceRatio  MedianCloseToOrigRatio  MedianDaysOnMarket  MedianListToContract  MedianContractToClose
                                              Compass  31815         1338000.0              751.53              1.00                    1.00                15.0                  18.0                   25.0
                               Coldwell Banker Realty  17310         1199000.0              688.65              1.00                    0.99                16.0                  21.0                   26.0
                                       NONMEMBER MRML  10745          500000.0              289.60              1.00                    0.99                26.0                  33.0                   31.0
                               Keller Williams Realty   7410          840000.0              534.30              1.00                    0.99                17.0                  24.0                   27.0
                                          Real Broker   7282          805000.0              543.60              1.00                    1.00                18.0                  25.0                   27.0
                         eXp Realty of California Inc   6129          835000.0              569.96              1.00                    1.00                19.0                  25.0                   28.0
                               First Team Real Estate   6097          900000.0              598.51              1.00                    1.00                14.0                  25.0                   28.0
                       eXp Realty of California, Inc.   5436          730500.0              494.51              1.00                    1.00                18.0                  25.0                   27.0
Berkshire Hathaway HomeServices California Properties   4745          989900.0              612.47              1.00                    0.99                21.0                  28.0                   28.0
                          Intero Real Estate Services   4073         1330000.0              808.46              1.01                    1.01                12.0                  12.0                   25.0

seg_school_district: 355 groups
            SchoolDistrict  Sales  MedianClosePrice  MedianPricePerSqFt  MedianPriceRatio  MedianCloseToOrigRatio  MedianDaysOnMarket  MedianListToContract  MedianContractToClose
       Los Angeles Unified  48808          981230.0              644.23              1.00                    0.99                21.0                  26.0                   30.0
         San Diego Unified  17416          930000.0              710.23              1.00                    0.99                14.0                  19.0                   25.0
        Capistrano Unified  10022         1369000.0              693.78              1.00                    0.99                16.0                  27.0                   28.0
      Desert Sands Unified   9276          590000.0              327.54              0.98                    0.96                50.0                  57.0                   13.0
      Palm Springs Unified   8806          568824.5              344.58              0.98                    0.96                49.0                  52.0                   23.0
      Grossmont Union High   8313          799000.0              511.70              1.00                    1.00                13.0                  20.0                   27.0
         Perris Union High   7141          575000.0              288.32              1.00                    1.00                24.0                  32.0                   31.0
Antelope Valley Union High   7076          490000.0              276.27              1.00                    1.00                25.0                  30.0                   34.0
  Chaffey Joint Union High   6833          706000.0              423.86              1.00                    1.00                17.0                  25.0                   31.0
        Long Beach Unified   6720          850000.0              643.17              1.00                    1.00                15.0                  27.0                   30.0
'''