import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import itertools

# Connect Database
engine = create_engine('postgresql://postgres:econ_finalproject@34.57.181.108:5432/yelp')

# Query fault counts with business names included
query_fault_counts = """
SELECT 
    b.name AS business_name,
    r.business_id,
    r.fault_type,
    DATE_PART('quarter', r.date) AS quarter,
    COUNT(*) AS repair_count
FROM reviews r
JOIN business b ON r.business_id = b.business_id
WHERE fault_type IS NOT NULL
GROUP BY b.name, r.business_id, r.fault_type, DATE_PART('quarter', r.date)
ORDER BY b.name, quarter, r.fault_type;
"""

print("Loading fault counts from database...")
fault_counts = pd.read_sql(query_fault_counts, engine)
print("Data loaded successfully!")

# Generate a CSV file with business name and other details
output_file = "/Users/xuchengyang/Desktop/fault_counts_with_business_names.csv"
fault_counts.to_csv(output_file, index=False)
print(f"CSV file saved to {output_file}")

# Visualization: Fill missing combinations of quarters and fault types
all_quarters = sorted(fault_counts["quarter"].unique())
all_faults = sorted(fault_counts["fault_type"].unique())
full_index = pd.DataFrame(
    list(itertools.product(all_quarters, all_faults)),
    columns=["quarter", "fault_type"]
)

fault_counts_full = (
    full_index.merge(fault_counts, on=["quarter", "fault_type"], how="left")
    .fillna({"repair_count": 0})
)

# Sort fault types by total repair count for better visualization
fault_order = (
    fault_counts_full.groupby("fault_type")["repair_count"]
    .sum()
    .sort_values(ascending=False)
    .index
)

# Color palette
color_palette = sns.color_palette("Set2", n_colors=len(fault_order))

# Visualization: Barplot
plt.figure(figsize=(12, 6))
sns.barplot(
    data=fault_counts_full,
    x="quarter",
    y="repair_count",
    hue="fault_type",
    palette=color_palette,
    hue_order=fault_order,
    errorbar=None
)
plt.xticks(ticks=[0, 1, 2, 3], labels=["1", "2", "3", "4"])
plt.title("Repair Count per Fault Type by Quarter")
plt.xlabel("Quarter")
plt.ylabel("Repair Count")
plt.legend(title="Fault Type (Sorted)", loc='upper right', bbox_to_anchor=(1.2, 1))
plt.tight_layout()
plt.show()
