"""Create dashboard-style chart images (one per report page) in results/."""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/clean_sales.csv", parse_dates=["Order Date", "Month"])
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
BLUE, RED, GREY = "#2b6cb0", "#d64545", "#8a94a6"
def money(x, _):
    sign = "-" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x/1e6:.1f}M" if x >= 1e6 else f"{sign}${x/1e3:.0f}K"
fmt = plt.FuncFormatter(money)


def kpi_row(fig, data):
    s, p = data["Sales"].sum(), data["Profit"].sum()
    items = [("Total Sales", f"${s/1e6:.2f}M"), ("Total Profit", f"${p/1e6:.2f}M"),
             ("Profit Margin", f"{p/s*100:.1f}%"), ("Orders", f"{data['Order ID'].nunique():,}")]
    for i, (name, val) in enumerate(items):
        fig.text(0.14 + i * 0.22, 0.90, val, ha="center", fontsize=20, weight="bold", color=BLUE)
        fig.text(0.14 + i * 0.22, 0.86, name, ha="center", fontsize=10, color=GREY)


# ---- Page 1: Overview ----
fig = plt.figure(figsize=(14, 8))
fig.suptitle("Sales Overview", x=0.02, ha="left", fontsize=16, weight="bold", y=1.0)
kpi_row(fig, df)
ax = fig.add_axes([0.06, 0.1, 0.55, 0.68])
m = df.groupby("Month")[["Sales", "Profit"]].sum()
ax.plot(m.index, m["Sales"], color=BLUE, label="Sales", lw=2)
ax.plot(m.index, m["Profit"], color="#2f9e6e", label="Profit", lw=2)
ax.yaxis.set_major_formatter(fmt); ax.set_title("Monthly Sales & Profit", loc="left"); ax.legend(frameon=False)
ax = fig.add_axes([0.70, 0.1, 0.27, 0.68])
y = df.groupby("Year")["Sales"].sum()
bars = ax.bar(y.index.astype(str), y.values, color=BLUE)
growth = y.pct_change() * 100
for b, g in zip(bars, growth):
    if pd.notna(g):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"+{g:.0f}%", ha="center", va="bottom")
ax.yaxis.set_major_formatter(fmt); ax.set_title("Yearly Sales (YoY growth)", loc="left")
fig.savefig("results/1_overview.png", dpi=120); plt.close(fig)

# ---- Page 2: Regions ----
fig, axs = plt.subplots(1, 3, figsize=(14, 6), gridspec_kw={"width_ratios": [1, 1, 1.2]})
fig.suptitle("Sales by Market and Region", x=0.02, ha="left", fontsize=16, weight="bold")
mk = df.groupby("Market")["Sales"].sum().sort_values()
axs[0].barh(mk.index, mk.values, color=BLUE); axs[0].xaxis.set_major_formatter(fmt)
axs[0].set_title("Sales by Market", loc="left")
rg = df.assign(Region=df["Region"] + " (" + df["Market"] + ")").groupby("Region")[["Sales", "Profit"]].sum().sort_values("Sales")
idx = range(len(rg))
axs[1].barh([i + 0.2 for i in idx], rg["Sales"], 0.4, color=BLUE, label="Sales")
axs[1].barh([i - 0.2 for i in idx], rg["Profit"], 0.4, color="#2f9e6e", label="Profit")
axs[1].set_yticks(list(idx)); axs[1].set_yticklabels(rg.index); axs[1].xaxis.set_major_formatter(fmt)
axs[1].set_title("Sales & Profit by Region", loc="left"); axs[1].legend(frameon=False)
co = df.groupby("Country")[["Sales", "Profit"]].sum().nlargest(10, "Sales")
axs[2].axis("off"); axs[2].set_title("Top 10 Countries", loc="left")
tbl = axs[2].table(cellText=[[c, f"${r.Sales/1e3:,.0f}K", f"${r.Profit/1e3:,.0f}K", f"{r.Profit/r.Sales*100:.1f}%"]
                             for c, r in co.iterrows()],
                   colLabels=["Country", "Sales", "Profit", "Margin"], loc="center", cellLoc="left", colWidths=[0.4, 0.2, 0.2, 0.2])
tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1, 1.6)
fig.tight_layout(); fig.savefig("results/2_regions.png", dpi=120); plt.close(fig)

# ---- Page 3: Products ----
fig, axs = plt.subplots(1, 3, figsize=(14, 6), gridspec_kw={"width_ratios": [1, 1, 1.4]})
fig.suptitle("Product Performance", x=0.02, ha="left", fontsize=16, weight="bold")
cat = df.groupby("Category")[["Sales", "Profit"]].sum()
axs[0].pie(cat["Sales"], labels=cat.index, autopct="%1.0f%%", colors=[BLUE, "#6fa8dc", "#a9c9ea"],
           wedgeprops={"width": 0.45})
axs[0].set_title("Sales Share by Category", loc="left")
axs[1].bar(cat.index, cat["Profit"], color=BLUE); axs[1].yaxis.set_major_formatter(fmt)
axs[1].set_title("Profit by Category", loc="left"); axs[1].tick_params(axis="x", rotation=20)
sub = df.groupby("Sub-Category")["Profit"].sum().sort_values()
axs[2].barh(sub.index, sub.values, color=[RED if v < 0 else BLUE for v in sub.values])
axs[2].xaxis.set_major_formatter(fmt); axs[2].set_title("Profit by Sub-Category (red = loss)", loc="left")
fig.tight_layout(); fig.savefig("results/3_products.png", dpi=120); plt.close(fig)

# ---- Page 4: Discount impact ----
fig, axs = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Discount Impact on Profit", x=0.02, ha="left", fontsize=16, weight="bold")
d = df.assign(D=((df["Discount"] * 10).round() * 10).astype(int)).groupby("D")[["Sales", "Profit"]].sum()
axs[0].bar(d.index.astype(str) + "%", d["Profit"] / d["Sales"] * 100,
           color=[RED if v < 0 else BLUE for v in d["Profit"]])
axs[0].set_title("Profit Margin by Discount Level (%)", loc="left"); axs[0].axhline(0, color="black", lw=0.8)
sc = df.groupby("Sub-Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Qty=("Quantity", "sum"))
axs[1].scatter(sc["Sales"], sc["Profit"], s=sc["Qty"] / 20, color=BLUE, alpha=0.6)
for n, r in sc.iterrows():
    axs[1].annotate(n, (r.Sales, r.Profit), fontsize=8, xytext=(4, 4), textcoords="offset points")
axs[1].xaxis.set_major_formatter(fmt); axs[1].yaxis.set_major_formatter(fmt)
axs[1].set_title("Sales vs Profit by Sub-Category", loc="left"); axs[1].axhline(0, color="black", lw=0.8)
fig.tight_layout(); fig.savefig("results/4_discount_impact.png", dpi=120); plt.close(fig)
print("Saved 4 images in results/")
