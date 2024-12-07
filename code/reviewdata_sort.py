import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd
import json
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
from sqlalchemy import create_engine
from sqlalchemy import text

# load_dotenv()

# 
# db_config = {
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT"),
# }

# Download NLTK data (needed for first-time use)
nltk.download('punkt')
nltk.download('stopwords')

# Initialize NLP tools
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

# Load dictionary data from JSON file
def load_fault_dict_from_json(json_path):
    with open(json_path, "r") as file:

        return json.load(file)

# Process dictionary data and apply stemming
def process_fault_dict(fault_dict):
    processed_dict = {}
    for key, values in fault_dict.items():
        processed_dict[key] = [stemmer.stem(value.lower()) for value in values]
    return processed_dict

# Define a function to extract fault type by matching stemmed keywords
def extract_fault_type(text, processed_dict):
    # Clean and stem input text
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())  # Remove special characters
    words = [stemmer.stem(word) for word in text.split() if word not in stop_words]

    # Match stemmed keywords with processed dictionary
    for key, values in processed_dict.items():
        if any(word in values for word in words):
            return key
    return None

# Database configuration
db_config = {
    "dbname": "yelp",
    "user": "postgres",
    "password": "econ_finalproject",
    "host": "34.57.181.108",
    "port": 5432
}

# Connect to the database using Pandas
engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

# Load dictionary and process it for stemming
json_path = "/Users/wusongyang/final-project/auto_parts_synonyms.json"  # Replace with the actual path
fault_dict = load_fault_dict_from_json(json_path)
processed_fault_dict = process_fault_dict(fault_dict)

# Load review table
reviews_df = pd.read_sql("SELECT review_id, business_id, text, date FROM reviews", con=engine)

# Clean the text column and extract fault_type
reviews_df["fault_type"] = reviews_df["text"].apply(lambda x: extract_fault_type(x, processed_fault_dict))

# Print the first few rows of the dataset f (with the new column fault_type)
# print(reviews_df.iloc[100:200])
# Update database: add the new column fault_type

with engine.begin() as conn:
    # Ensure the SQL is a valid executable object
    conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS fault_type TEXT"))

    # Batch update the database using a loop
    for _, row in reviews_df.iterrows():
        conn.execute(
            text("UPDATE reviews SET fault_type = :fault_type WHERE review_id = :review_id"),
            {"fault_type": row["fault_type"], "review_id": row["review_id"]}
        )

print("Reviews table updated with fault_type!")