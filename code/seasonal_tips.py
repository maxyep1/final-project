import pandas as pd

# File path
file_path = "/Users/xuchengyang/Desktop/seasonal_fault_trends.csv"

# Read CSV file and rename columns
df = pd.read_csv(file_path, header=1)
df.columns = ['fault_type', '1', '2', '3', '4']

# Ensure numeric types for seasonal columns
for season in ['1', '2', '3', '4']:
    df[season] = df[season].astype(float)

# Calculate annual average for each fault type
df["annual_average"] = df[['1', '2', '3', '4']].mean(axis=1)

# Calculate seasonal deviation from annual average
for season in ['1', '2', '3', '4']:
    df[f"probability_{season}"] = df[season] / df["annual_average"]

# Create a new DataFrame to store top 3 faults per season
top3_parts = pd.DataFrame()

# Extract top 3 faults per season
for season in ['1', '2', '3', '4']:
    top_parts = df.nlargest(3, f"probability_{season}")[["fault_type", f"probability_{season}"]]
    top_parts["season"] = f"Season_{season}"
    top_parts.rename(columns={f"probability_{season}": "failure_probability"}, inplace=True)
    top3_parts = pd.concat([top3_parts, top_parts], ignore_index=True)

# Save the results to a CSV file
output_path = "/Users/xuchengyang/Desktop/seasonal_tips_top3.csv"
top3_parts.to_csv(output_path, index=False)

# Print confirmation message
print(f"Results saved")
