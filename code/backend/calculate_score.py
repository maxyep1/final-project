"""
This function calculates the composite score for each repair shop.
The formula combines the repair count and average rating:
composite_score = log(1 + repair_count) * avg_rating
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to Database
engine = create_engine('postgresql://postgres:econ_finalproject@34.57.181.108:5432/yelp')

def calculate_composite_scores():
    # Query to get repair count, average rating, and business name
    query = """
    SELECT 
        r.business_id,
        b.name AS business_name,
        r.fault_type,
        COUNT(*) AS repair_count,
        b.stars AS avg_rating
    FROM reviews r
    JOIN business b ON r.business_id = b.business_id
    GROUP BY r.business_id, b.name, r.fault_type, b.stars
    ORDER BY r.business_id, fault_type;
    """
    
    print("Loading data from database...")
    shop_fault_data = pd.read_sql(query, engine)
    print("Data loaded successfully!")

    # Filter out missing business_name or fault_type
    print("Checking for missing business_name or fault_type...")
    shop_fault_data = shop_fault_data.dropna(subset=["business_name", "fault_type"])
    print(f"Remaining rows after filtering: {len(shop_fault_data)}")

    # Handle missing values for repair_count and avg_rating
    print("Checking for missing values in repair_count or avg_rating...")
    shop_fault_data["repair_count"].fillna(0, inplace=True)
    shop_fault_data["avg_rating"].fillna(shop_fault_data["avg_rating"].mean(), inplace=True)

    # Calculate composite scores using a log-based formula
    print("Calculating composite scores...")
    shop_fault_data["composite_score"] = (
        np.log1p(shop_fault_data["repair_count"]) * shop_fault_data["avg_rating"]
    )

    # Sort by composite score
    shop_fault_data = shop_fault_data.sort_values(by="composite_score", ascending=False)

    # Save results to a CSV file
    output_file = "/Users/xuchengyang/Desktop/shop_fault_composite_scores.csv"
    shop_fault_data.to_csv(output_file, index=False)
    print(f"Composite scores saved to {output_file}")

    return shop_fault_data

def visualize_by_fault_type(data):
    # Drop any remaining NaN values
    data = data.dropna()

    fault_types = data["fault_type"].unique()

    for fault in fault_types:
        fault_data = data[data["fault_type"] == fault]

        top_10 = fault_data.sort_values(by="composite_score", ascending=False).head(10)

        print(f"Visualizing top businesses for fault type: {fault}")
        plt.figure(figsize=(12, 8))
        sns.barplot(
            data=top_10,
            x="business_name",
            y="composite_score",
            palette="Set2",
            dodge=False,
            width=0.8
        )
        plt.title(f"Top 10 Businesses by Composite Score ({fault})")
        plt.xlabel("Business Name")
        plt.ylabel("Composite Score")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Calculate scores
    scores_df = calculate_composite_scores()

    visualize_by_fault_type(scores_df)
