import pandas as pd

# -----------------------------------------------------------------------------------
# Extreme values in price, price per square footage, close to list ratio, or days on 
# market can distort market averages and trends.
# Implement a statistical method to identify and remove these records.
# -----------------------------------------------------------------------------------

# Method: Interquartile Range (IQR): removes records that fall outside a defined statistical range

df_sold = pd.read_csv("Sold_Features.csv")