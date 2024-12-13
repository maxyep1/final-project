import pandas as pd
import json
import psycopg2
from dotenv import load_dotenv
import os

# Load
load_dotenv()

# Database
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Path
business_id_file = "../data/auto_repair_businesses_PA_filtered.csv"
review_file = "../data/yelp_academic_dataset_review.json"


# Read business_id file
business_ids = pd.read_csv(business_id_file)["business_id"].tolist()

# Connect to PostgreSQL
try:
    client = psycopg2.connect(**db_config)
    cursor = client.cursor()
except Exception as e:
    exit()

create_table_query = """
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(255),
    business_id VARCHAR(255),
    stars INTEGER,
    text TEXT,
    date DATE
);
"""
cursor.execute(create_table_query)
client.commit()

try:
    with open(review_file, 'r') as f:
        total_lines = sum(1 for _ in open(review_file, 'r'))  
        f.seek(0)  
        processed_lines = 0
        for line in f:
            review = json.loads(line)
            processed_lines += 1
            if review["business_id"] in business_ids:
                for key in ["user_id", "useful", "funny", "cool"]:
                    review.pop(key, None)
                data = (
                    review["review_id"],
                    review["business_id"],
                    review["stars"],
                    review["text"],
                    review["date"]
                )
                insert_query = """
                    INSERT INTO reviews (review_id, business_id, stars, text, date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, data)
            if processed_lines % 10000 == 0:
        client.commit()
except Exception as e:
    client.rollback()
finally:
    cursor.close()
    client.close()
    print("数据库连接已关闭。")
