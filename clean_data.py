"""Clean the Global Superstore data with simple Pandas steps.

Input : data/Global_Superstore2.csv   (from Kaggle)
Output: data/clean_sales.csv          (load this into Power BI)
"""
import pandas as pd

df = pd.read_csv("data/Global_Superstore2.csv", encoding="latin-1")
print("Raw rows:", len(df))
steps = {}

# 1. remove exact duplicate rows
before = len(df)
df = df.drop_duplicates()
steps["Duplicate rows removed"] = before - len(df)

# 2. fix text columns: strip extra spaces
for col in ["Segment", "Market", "Region", "Country", "State", "City", "Category", "Sub-Category"]:
    df[col] = df[col].str.strip()

# 3. convert dates (file uses day-month-year)
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y")

# 4. drop rows missing key fields or with invalid values
before = len(df)
df = df.dropna(subset=["Order ID", "Order Date", "Sales", "Profit", "Region", "Category"])
df = df[(df["Quantity"] > 0) & (df["Sales"] > 0)]
steps["Invalid rows removed"] = before - len(df)

# 5. Postal Code is only present for US orders -> fill the rest with "N/A" (as text)
df["Postal Code"] = df["Postal Code"].apply(lambda x: "N/A" if pd.isna(x) else str(int(x)))

# 6. add helpful columns for analysis
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

# 7. round money columns
df[["Sales", "Profit", "Shipping Cost"]] = df[["Sales", "Profit", "Shipping Cost"]].round(2)

df.to_csv("data/clean_sales.csv", index=False)
for k, v in steps.items():
    print(f"{k}: {v}")
print("Clean rows:", len(df), "-> saved data/clean_sales.csv")
print("Years:", df["Year"].min(), "to", df["Year"].max())
