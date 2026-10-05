# Walmart sales analysis project
# looking at sales and e-commerce performance from 2024 to 2026

from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt


# project folders
project_folder = Path(__file__).resolve().parent

data_folder = project_folder / "data"
images_folder = project_folder / "images"

data_folder.mkdir(exist_ok=True)
images_folder.mkdir(exist_ok=True)


# my original walmart data
input_file = data_folder / "walmart_sales_2026.csv"


# checking the file before running the analysis
if not input_file.exists():
    print("I could not find walmart_sales_2026.csv")
    print("Make sure it is inside the data folder.")
    raise FileNotFoundError(input_file)


# reading the csv with pandas
df = pd.read_csv(input_file)


print("\n----------------------------------------")
print("WALMART SALES ANALYSIS")
print("----------------------------------------")

print("\nOriginal data:")
print(df)


# cleaning the column names just in case there are extra spaces
df.columns = df.columns.str.strip()


# columns I need for this project
needed_columns = [
    "Fiscal_Year",
    "Segment",
    "Net_Sales_Millions",
    "Ecommerce_Sales_Millions"
]


# checking if something is missing from the csv
missing_columns = []

for column in needed_columns:
    if column not in df.columns:
        missing_columns.append(column)


if missing_columns:
    print("\nMissing columns:")
    print(missing_columns)

    print("\nColumns found in the CSV:")
    print(df.columns.tolist())

    raise ValueError("Some required columns are missing.")


# cleaning segment names
df["Segment"] = df["Segment"].astype(str).str.strip()


# making sure these columns are numbers
df["Fiscal_Year"] = pd.to_numeric(
    df["Fiscal_Year"],
    errors="coerce"
)

df["Net_Sales_Millions"] = pd.to_numeric(
    df["Net_Sales_Millions"],
    errors="coerce"
)

df["Ecommerce_Sales_Millions"] = pd.to_numeric(
    df["Ecommerce_Sales_Millions"],
    errors="coerce"
)


# removing rows that do not have the main information I need
df = df.dropna(
    subset=[
        "Fiscal_Year",
        "Segment",
        "Net_Sales_Millions",
        "Ecommerce_Sales_Millions"
    ]
)


df["Fiscal_Year"] = df["Fiscal_Year"].astype(int)


# putting each segment and year in order
df = df.sort_values(
    ["Segment", "Fiscal_Year"]
).reset_index(drop=True)


# converting sales from millions to billions
# billions are easier to read in the dashboard
df["Net_Sales_Billions"] = (
    df["Net_Sales_Millions"] / 1000
)

df["Ecommerce_Sales_Billions"] = (
    df["Ecommerce_Sales_Millions"] / 1000
)


# checking how much of total sales came from e-commerce
df["Ecommerce_Share_Percent"] = (
    df["Ecommerce_Sales_Millions"]
    / df["Net_Sales_Millions"]
    * 100
)


# year over year sales growth for each segment
df["Sales_Growth_Percent"] = (
    df.groupby("Segment")["Net_Sales_Millions"]
    .pct_change()
    * 100
)


# year over year e-commerce growth
df["Ecommerce_Growth_Percent"] = (
    df.groupby("Segment")["Ecommerce_Sales_Millions"]
    .pct_change()
    * 100
)


# saving the complete analyzed data
analyzed_file = data_folder / "walmart_sales_analyzed.csv"

df.to_csv(
    analyzed_file,
    index=False
)


print("\nCleaned and analyzed data:")
print(df.round(2))


# --------------------------------------------------
# company level summary
# --------------------------------------------------

company_summary = (
    df.groupby("Fiscal_Year", as_index=False)
    .agg(
        Total_Net_Sales_Billions=(
            "Net_Sales_Billions",
            "sum"
        ),

        Total_Ecommerce_Sales_Billions=(
            "Ecommerce_Sales_Billions",
            "sum"
        )
    )
)


# overall e-commerce share
company_summary["Ecommerce_Share_Percent"] = (
    company_summary["Total_Ecommerce_Sales_Billions"]
    / company_summary["Total_Net_Sales_Billions"]
    * 100
)


# company sales growth compared with the previous year
company_summary["YoY_Sales_Growth_Percent"] = (
    company_summary["Total_Net_Sales_Billions"]
    .pct_change()
    * 100
)


# company e-commerce growth
company_summary["YoY_Ecommerce_Growth_Percent"] = (
    company_summary["Total_Ecommerce_Sales_Billions"]
    .pct_change()
    * 100
)


company_summary.to_csv(
    data_folder / "company_summary.csv",
    index=False
)


# --------------------------------------------------
# 2026 segment analysis
# --------------------------------------------------

fy2026 = df[
    df["Fiscal_Year"] == 2026
].copy()


total_2026_sales = fy2026[
    "Net_Sales_Billions"
].sum()


# percent contribution from each segment
fy2026["Sales_Contribution_Percent"] = (
    fy2026["Net_Sales_Billions"]
    / total_2026_sales
    * 100
)


fy2026.to_csv(
    data_folder / "fy2026_segment_summary.csv",
    index=False
)


# saving a smaller file just for growth analysis
growth_analysis = df[
    [
        "Fiscal_Year",
        "Segment",
        "Sales_Growth_Percent",
        "Ecommerce_Growth_Percent",
        "Ecommerce_Share_Percent"
    ]
].copy()


growth_analysis.to_csv(
    data_folder / "segment_growth_analysis.csv",
    index=False
)


# --------------------------------------------------
# showing the main 2026 numbers
# --------------------------------------------------

fy2026_company = company_summary[
    company_summary["Fiscal_Year"] == 2026
].iloc[0]


print("\n----------------------------------------")
print("FY2026 MAIN RESULTS")
print("----------------------------------------")

print(
    f"Total Net Sales: "
    f"${fy2026_company['Total_Net_Sales_Billions']:.2f}B"
)

print(
    f"Total E-commerce Sales: "
    f"${fy2026_company['Total_Ecommerce_Sales_Billions']:.2f}B"
)

print(
    f"YoY Sales Growth: "
    f"{fy2026_company['YoY_Sales_Growth_Percent']:.2f}%"
)

print(
    f"E-commerce Share: "
    f"{fy2026_company['Ecommerce_Share_Percent']:.1f}%"
)


print("\n2026 segment results:")

print(
    fy2026[
        [
            "Segment",
            "Net_Sales_Billions",
            "Ecommerce_Sales_Billions",
            "Sales_Contribution_Percent"
        ]
    ].round(2)
)


# ==================================================
# CHART 1
# net sales trend
# ==================================================

fig1 = plt.figure(figsize=(10, 6))

for segment in df["Segment"].unique():

    segment_data = df[
        df["Segment"] == segment
    ]

    plt.plot(
        segment_data["Fiscal_Year"],
        segment_data["Net_Sales_Billions"],
        marker="o",
        linewidth=2,
        label=segment
    )


plt.title(
    "Walmart Net Sales Trend by Segment"
)

plt.xlabel(
    "Fiscal Year"
)

plt.ylabel(
    "Net Sales (Billions USD)"
)

plt.xticks(
    [2024, 2025, 2026]
)

plt.grid(
    alpha=0.3
)

plt.legend()

plt.tight_layout()


plt.savefig(
    images_folder / "sales_growth_2024_2026.png",
    dpi=300,
    bbox_inches="tight"
)


# ==================================================
# CHART 2
# e-commerce sales trend
# ==================================================

fig2 = plt.figure(figsize=(10, 6))

for segment in df["Segment"].unique():

    segment_data = df[
        df["Segment"] == segment
    ]

    plt.plot(
        segment_data["Fiscal_Year"],
        segment_data["Ecommerce_Sales_Billions"],
        marker="o",
        linewidth=2,
        label=segment
    )


plt.title(
    "E-commerce Sales Trend by Segment"
)

plt.xlabel(
    "Fiscal Year"
)

plt.ylabel(
    "E-commerce Sales (Billions USD)"
)

plt.xticks(
    [2024, 2025, 2026]
)

plt.grid(
    alpha=0.3
)

plt.legend()

plt.tight_layout()


plt.savefig(
    images_folder / "ecommerce_growth.png",
    dpi=300,
    bbox_inches="tight"
)


# ==================================================
# CHART 3
# e-commerce share
# ==================================================

fig3 = plt.figure(figsize=(10, 6))

for segment in df["Segment"].unique():

    segment_data = df[
        df["Segment"] == segment
    ]

    plt.plot(
        segment_data["Fiscal_Year"],
        segment_data["Ecommerce_Share_Percent"],
        marker="o",
        linewidth=2,
        label=segment
    )


plt.title(
    "E-commerce Share of Net Sales"
)

plt.xlabel(
    "Fiscal Year"
)

plt.ylabel(
    "E-commerce Share (%)"
)

plt.xticks(
    [2024, 2025, 2026]
)

plt.grid(
    alpha=0.3
)

plt.legend()

plt.tight_layout()


plt.savefig(
    images_folder / "ecommerce_share.png",
    dpi=300,
    bbox_inches="tight"
)


# ==================================================
# CHART 4
# 2026 net sales by segment
# ==================================================

fy2026_sorted = fy2026.sort_values(
    "Net_Sales_Billions",
    ascending=True
)


fig4 = plt.figure(figsize=(10, 6))


bars = plt.barh(
    fy2026_sorted["Segment"],
    fy2026_sorted["Net_Sales_Billions"]
)


plt.title(
    "FY2026 Net Sales by Segment"
)

plt.xlabel(
    "Net Sales (Billions USD)"
)

plt.ylabel(
    "Segment"
)


# adding the number beside each bar
for bar in bars:

    value = bar.get_width()

    plt.text(
        value + 3,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}",
        va="center"
    )


plt.tight_layout()


plt.savefig(
    images_folder / "net_sales_by_segment.png",
    dpi=300,
    bbox_inches="tight"
)


# ==================================================
# CHART 5
# 2026 sales contribution
# ==================================================

fig5 = plt.figure(figsize=(8, 8))


plt.pie(
    fy2026["Net_Sales_Billions"],
    labels=fy2026["Segment"],
    autopct="%1.1f%%",
    startangle=90
)


plt.title(
    "FY2026 Sales Contribution by Segment"
)

plt.tight_layout()


plt.savefig(
    images_folder / "fy2026_segment_share.png",
    dpi=300,
    bbox_inches="tight"
)


# --------------------------------------------------
# checking for my Power BI dashboard
# --------------------------------------------------

powerbi_files = list(
    project_folder.rglob("*.pbix")
)


if powerbi_files:

    powerbi_file = powerbi_files[0]

    print("\nPower BI dashboard found:")
    print(powerbi_file)

    # this works on Windows and opens the dashboard
    try:
        os.startfile(powerbi_file)

        print(
            "Opening my Power BI dashboard..."
        )

    except Exception as error:

        print(
            "Power BI could not open automatically."
        )

        print(error)

else:

    print(
        "\nI could not find a .pbix file "
        "inside this project folder."
    )

    print(
        "Put Walmart_Sales_Dashboard.pbix "
        "inside the project or powerbi folder."
    )


# --------------------------------------------------
# finished
# --------------------------------------------------

print("\n----------------------------------------")
print("ANALYSIS COMPLETE")
print("----------------------------------------")

print(
    "\nThe updated CSV files were saved "
    "inside the data folder."
)

print(
    "The charts were saved inside "
    "the images folder."
)

print(
    "\nClose the chart windows when "
    "you are finished looking at them."
)


# this is what makes the Python charts appear
plt.show()