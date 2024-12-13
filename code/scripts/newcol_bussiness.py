import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv


# Load
load_dotenv()

# Connect to Database
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def fetch_reviews():
    return pd.read_sql("SELECT business_id, fault_type FROM reviews", con=engine)


# print("reviews_df head:")
# print(reviews_df.head())
# print("reviews_df shape:", reviews_df.shape)


def process_fault_counts(reviews_df):
    """
    Count the number of occurrences of business_id based on the fault_type and return a DataFrame containing the count.
    """
    fault_counts = (
        reviews_df.groupby(["business_id", "fault_type"])
        .size()
        .reset_index(name="count")
    )
    return fault_counts

def generate_business_stats(group):
    """
    past_businesses and best_business
    """
    if group.empty:
        return "unknown", "unknown"

    # Create the past_businesses string
    past_businesses = ",".join(f"{row['fault_type']}({row['count']})" for _, row in group.iterrows())
    
    # Identify the fault_type with the highest occurrence
    best_business = group.loc[group["count"].idxmax(), "fault_type"]
    return past_businesses, best_business


def build_business_stats(fault_counts):
    """
    Generate business statistics based on fault_comunts and return a DataFrame
    """
    business_stats = []
    for business_id, group in fault_counts.groupby("business_id"):
        if group["fault_type"].isnull().all():
            business_stats.append((business_id, "unknown", "unknown"))
        else:
            past_businesses, best_business = generate_business_stats(group)
            business_stats.append((business_id, past_businesses, best_business))

    business_stats_df = pd.DataFrame(business_stats, columns=["business_id", "past_businesses", "best_business"])
    return business_stats_df




def fetch_business_table():
    """
   Read the 'business' table from the database and return a DataFrame.
    """
    return pd.read_sql("SELECT * FROM business", con=engine)






# def merge_and_fill_data(business_df, business_stats_df):
#     """
#    Merge the 'business' and statistical information into a DataFrame, and fill in missing values.
#     """
#     updated_business_df = business_df.merge(business_stats_df, on="business_id", how="left")
#     updated_business_df["past_businesses"].fillna("unknown", inplace=True)
#     updated_business_df["best_business"].fillna("unknown", inplace=True)
#     return updated_business_df

def merge_and_update_diff(business_df, business_stats_df):
    """
    Merge the 'business' and statistical information into a DataFrame, updating only the differences between the new and old columns.
    """
    if "past_businesses" not in business_df.columns:
        business_df["past_businesses"] = None

    if "best_business" not in business_df.columns:
        business_df["best_business"] = None

    merged_df = business_df.merge(
        business_stats_df,
        on="business_id",
        how="left",
        suffixes=("", "_new") 
    )

    merged_df["past_businesses"] = merged_df.apply(
        lambda row: row["past_businesses_new"]
        if pd.notnull(row["past_businesses_new"]) and row["past_businesses"] != row["past_businesses_new"]
        else row["past_businesses"],
        axis=1
    )

    merged_df["best_business"] = merged_df.apply(
        lambda row: row["best_business_new"]
        if pd.notnull(row["best_business_new"]) and row["best_business"] != row["best_business_new"]
        else row["best_business"],
        axis=1
    )

    merged_df.drop(columns=["past_businesses_new", "best_business_new"], inplace=True)

    return merged_df






def main():
    """
   Main function: Process data and generate updated business tables.

    """
    global updated_business_df
    reviews_df = fetch_reviews()
    fault_counts = process_fault_counts(reviews_df)
    business_stats_df = build_business_stats(fault_counts)
    business_df = fetch_business_table()

    updated_business_df = merge_and_update_diff(business_df, business_stats_df)

    print(updated_business_df.head(50))
    # print(updated_business_df.iloc[100:200])

main()



# Update the database: add the new columns past_businesses and best_business
with engine.begin() as conn:
    # Add the new columns if they do not exist
    conn.execute(text("ALTER TABLE business ADD COLUMN IF NOT EXISTS past_businesses TEXT"))
    conn.execute(text("ALTER TABLE business ADD COLUMN IF NOT EXISTS best_business TEXT"))

    # Batch update the database using a loop
    for _, row in updated_business_df.iterrows():
        conn.execute(
            text("""
                UPDATE business
                SET past_businesses = :past_businesses,
                    best_business = :best_business
                WHERE business_id = :business_id
            """),
            {
                "past_businesses": row["past_businesses"],
                "best_business": row["best_business"],
                "business_id": row["business_id"]
            }
        )

print("Business table successfully updated with past_businesses and best_business!")






