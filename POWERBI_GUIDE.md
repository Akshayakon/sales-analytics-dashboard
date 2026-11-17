# Power BI Dashboard Guide

Power BI reports (.pbix) are built in Power BI Desktop, so follow these steps. Data is ready in `data/clean_sales.csv` (51,290 rows, 2011–2014).

## 1. Load data
1. Open Power BI Desktop, then **Home > Get data > Text/CSV**, and pick `data/clean_sales.csv`.
2. Click **Transform Data** and check the types:
   - `Order Date`, `Ship Date`, `Month`: **Date**
   - `Sales`, `Profit`, `Discount`, `Profit Margin %`: **Decimal number**
   - `Quantity`, `Year`, `Ship Days`: **Whole number**
3. **Close & Apply**. Rename the table to `Sales`.

## 2. Date table (for time charts)
**Modeling > New table**, then paste:
```DAX
Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2011,1,1), DATE(2014,12,31)),
    "Year", YEAR([Date]),
    "Month No", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "Year-Month", FORMAT([Date], "YYYY-MM"))
```
Then go to **Model view** and drag `Calendar[Date]` onto `Sales[Order Date]` (one-to-many). Mark it as a date table.

## 3. Measures
**Modeling > New measure** (create each one):
```DAX
Total Sales   = SUM(Sales[Sales])
Total Profit  = SUM(Sales[Profit])
Profit Margin = DIVIDE([Total Profit], [Total Sales])
Orders        = DISTINCTCOUNT(Sales[Order ID])
Avg Order Value = DIVIDE([Total Sales], [Orders])
Sales LY      = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Calendar'[Date]))
YoY Growth %  = DIVIDE([Total Sales] - [Sales LY], [Sales LY])
```
Format `Profit Margin` and `YoY Growth %` as percentages.

## 4. Report pages

### Page 1: Overview
| Visual | Fields |
|---|---|
| 4 **Cards** | Total Sales, Total Profit, Profit Margin, Orders |
| **Line chart** | X: `Calendar[Year-Month]`, Y: Total Sales, Total Profit |
| **Clustered column** | X: `Calendar[Year]`, Y: Total Sales (add YoY Growth % as data label or tooltip) |
| **Slicers** | Year, Region, Category, Segment |

### Page 2: Regions
| Visual | Fields |
|---|---|
| **Map** (filled map) | Location: Country, Values: Total Sales |
| **Bar chart** | Axis: Market, Values: Total Sales |
| **Clustered bar** | Axis: Region (13 values), Values: Total Sales, Total Profit |
| **Table** | Country, Total Sales, Total Profit, Profit Margin (add conditional formatting) |

### Page 3: Products
| Visual | Fields |
|---|---|
| **Donut** | Legend: Category, Values: Total Sales |
| **Bar chart** | Axis: Sub-Category, Values: Total Profit. Under Format > Colors, use conditional "Rules" so negative is red |
| **Matrix** | Rows: Category > Sub-Category, Values: Total Sales, Total Profit, Profit Margin |

### Page 4: Discount Impact
| Visual | Fields |
|---|---|
| **Column chart** | Axis: Discount, Values: Profit Margin |
| **Scatter** | X: Total Sales, Y: Total Profit, Details: Sub-Category, Size: Quantity |
| **Text box** | Key findings and inventory recommendation (see below) |

## 5. Polish
- Use **View > Themes** to pick one consistent theme.
- Use **View > Sync slicers** so filters apply to all pages.
- Add page navigation buttons (**Insert > Buttons > Navigator**).
- Use a title bar on each page and tidy the alignment.

## 6. Insights to put in the report
- APAC and EU lead on sales; Canada is the smallest market.
- Technology is the most profitable category; Furniture is the weakest.
- Tables is the only sub-category that loses money overall.
- Orders with discounts of 30% or more lose money; discounts of 0–20% earn about $2.3M profit combined.
- **Recommendation:** stock more high-profit sub-categories in the top regions, and cap discounts at 20% and review pricing on Tables.

## 7. Save and share
Save as `Sales_Dashboard.pbix` in this folder. Take a screenshot of each page and save them in the `results/` folder with these exact names, so the README shows them:
`1_overview.png`, `2_regions.png`, `3_products.png`, `4_discount_impact.png`
(Tip: in Power BI Desktop use **File > Export > Export to PDF**, or Windows `Win + Shift + S` to capture each page.) You can also **Publish** to Power BI Service (free account) to get a shareable link.
