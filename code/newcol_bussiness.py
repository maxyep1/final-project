import pandas as pd
from sqlalchemy import create_engine, text

# Database configuration
db_config = {
    "dbname": "yelp",
    "user": "postgres",
    "password": "econ_finalproject",
    "host": "34.57.181.108",
    "port": 5432
}

# Connect to the database using SQLAlchemy
engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

# Load the reviews table
reviews_df = pd.read_sql("SELECT business_id, fault_type FROM reviews", con=engine)

# Clean the data and count occurrences of different fault_types for each business_id
fault_counts = (
    reviews_df.groupby(["business_id", "fault_type"])
    .size()
    .reset_index(name="count")
)

# Build the past_businesses and best_business data
def generate_business_stats(group):
    if group.empty:
        return "unknown", "unknown"

    # Create the past_businesses string
    past_businesses = ",".join(f"{row['fault_type']}({row['count']})" for _, row in group.iterrows())
    
    # Identify the fault_type with the highest occurrence
    best_business = group.loc[group["count"].idxmax(), "fault_type"]
    return past_businesses, best_business

# Iterate through each group of business_id
business_stats = []
for business_id, group in fault_counts.groupby("business_id"):
    if group["fault_type"].isnull().all():
        business_stats.append((business_id, "unknown", "unknown"))
    else:
        past_businesses, best_business = generate_business_stats(group)
        business_stats.append((business_id, past_businesses, best_business))

# Create a new DataFrame with business stats
business_stats_df = pd.DataFrame(business_stats, columns=["business_id", "past_businesses", "best_business"])

# Load the business table
business_df = pd.read_sql("SELECT * FROM business", con=engine)

# Merge the new columns into the business table
updated_business_df = business_df.merge(business_stats_df, on="business_id", how="left")

# Fill unmatched business_ids with "unknown"
updated_business_df["past_businesses"].fillna("unknown", inplace=True)
updated_business_df["best_business"].fillna("unknown", inplace=True)

# Print the updated DataFrame for verification
# print(updated_business_df.head(50))
# print(updated_business_df.iloc[100:200])

# Update the database: add the new columns past_businesses and best_business
with engine.connect() as conn:
    # Add the new columns if they do not exist
    conn.execute(text("ALTER TABLE business ADD COLUMN IF NOT EXISTS past_businesses TEXT"))
    conn.execute(text("ALTER TABLE business ADD COLUMN IF NOT EXISTS best_business TEXT"))

    # Explicitly update the database row by row
    for _, row in updated_business_df.iterrows():
        conn.execute(
            text(
                "UPDATE business SET past_businesses = :past_businesses, best_business = :best_business WHERE business_id = :business_id"
            ),
            {
                "past_businesses": row["past_businesses"],
                "best_business": row["best_business"],
                "business_id": row["business_id"]
            }
        ) 
        conn.commit()

print("Business table successfully updated with past_businesses and best_business!")
