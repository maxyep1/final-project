import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# Database connection
engine = create_engine('postgresql://postgres:econ_finalproject@34.57.181.108:5432/yelp')

def analyze_seasonal_trends():
    """
    Analyze seasonal trends for fault types based on repair counts.
    """
    query = """
    SELECT 
        r.fault_type,
        DATE_PART('quarter', r.date) AS quarter,
        COUNT(*) AS repair_count
    FROM reviews r
    GROUP BY r.fault_type, DATE_PART('quarter', r.date)
    ORDER BY r.fault_type, quarter;
    """
    
    print("Loading data from database...")
    seasonal_data = pd.read_sql(query, engine)
    print("Data loaded successfully!")

    # Pivot the data for easier visualization
    seasonal_pivot = seasonal_data.pivot(
        index="fault_type", columns="quarter", values="repair_count"
    ).fillna(0)
    
    # Save the pivot table to a CSV file
    output_file = "/Users/xuchengyang/Desktop/seasonal_fault_trends.csv"
    seasonal_pivot.to_csv(output_file)
    print(f"Seasonal trends saved to {output_file}")

    return seasonal_data, seasonal_pivot

def visualize_seasonal_trends(seasonal_data):
    """
    Visualize the seasonal trends for fault types using a line chart.
    """
    plt.figure(figsize=(12, 8))
    sns.lineplot(
        data=seasonal_data,
        x="quarter",
        y="repair_count",
        hue="fault_type",
        marker="o"
    )
    plt.title("Seasonal Trends of Fault Types")
    plt.xlabel("Quarter")
    plt.ylabel("Repair Count")
    plt.legend(title="Fault Type", loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.tight_layout()
    plt.show()

def visualize_heatmap(seasonal_data):
    """
    Visualize seasonal trends using a heatmap for fault types and quarters.
    """
    # Pivot data for heatmap
    heatmap_data = seasonal_data.pivot_table(
        index="fault_type", columns="quarter", values="repair_count", aggfunc="sum"
    ).fillna(0)

    # Plot the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".0f",
        cmap="YlGnBu",
        cbar_kws={'label': 'Repair Count'}
    )
    plt.title("Seasonal Trends of Fault Types (Heatmap)")
    plt.xlabel("Quarter")
    plt.ylabel("Fault Type")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Analyze seasonal trends
    seasonal_data, seasonal_pivot = analyze_seasonal_trends()

    # Visualize seasonal trends with line chart
    visualize_seasonal_trends(seasonal_data)

    # Visualize seasonal trends with heatmap
    visualize_heatmap(seasonal_data)
