import pandas as pd;

# Load and concatenate all monthly MLS files from January 2024 through the 
# most recently completed calendar month into analysis-ready combined datasets
list_all_months = pd.DataFrame()
length = 0

for i in range(1, 13, 1):
    date = f"{i:02d}"
    df = pd.read_csv(f"data/CRMLSListing2024{date}.csv")
    length += len(df)
    list_all_months = pd.concat([list_all_months, df])

for i in range(1, 13, 1):
    date = f"{i:02d}"
    df = pd.read_csv(f"data/CRMLSListing2025{date}.csv")
    length += len(df)
    list_all_months = pd.concat([list_all_months, df])

for i in range(1, 9, 1):
    date = f"{i:02d}"
    df = pd.read_csv(f"data/CRMLSListing2026{date}.csv", encoding='cp1252', low_memory=False)
    length += len(df)
    list_all_months = pd.concat([list_all_months, df])

print(length)

sold_all_months = pd.DataFrame()
length = 0

for i in range(1, 13, 1):
    date = f"{i:02d}"
    df = pd.read_csv(f"data/CRMLSSold2024{date}.csv")
    length += len(df)
    sold_all_months = pd.concat([sold_all_months, df])

for i in range(1, 13, 1):
    date = f"{i:02d}"
    df = pd.read_csv(f"data/CRMLSSold2025{date}.csv")
    length += len(df)
    sold_all_months = pd.concat([sold_all_months, df])

for i in range(1, 9, 1):
    date = f"{i:02d}"
    df = pd.read_csv(f"data/CRMLSSold2026{date}.csv", encoding='cp1252', low_memory=False)
    length += len(df)
    sold_all_months = pd.concat([sold_all_months, df])

print(length)

sold_all_months_unfiltered = sold_all_months.to_csv("All_Months_Sold_Unfiltered.csv", index=False)
list_all_months = list_all_months[list_all_months.PropertyType == "Residential"]
print("After filter: " + str(len(list_all_months)))
sold_all_months = sold_all_months[sold_all_months.PropertyType== "Residential"]
print("After filter: " + str(len(sold_all_months)))

# Listing rows after concatenating: 990804
# Listing rows after filter: 630083

# Sold rows after concatenating: 714364
# Sold rows after filter: 480484

# list_all_months.to_csv("All_Months_Listing.csv", index=False)
# sold_all_months.to_csv("All_Months_Sold.csv", index=False)
