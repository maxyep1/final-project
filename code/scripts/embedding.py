import os
import pandas as pd
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

DATABASE_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
               f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URI)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_unembedded_reviews():
    query = text("""
    SELECT review_id, text
    FROM reviews
    WHERE embedding IS NULL
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    return pd.DataFrame(rows, columns=["review_id", "text"])

def generate_embeddings(df):
    embeddings = []
    for txt in tqdm(df["text"], desc="Generating embeddings"):
        vector = model.encode(txt)
        embeddings.append(vector.tolist())
    df["embedding"] = embeddings
    return df

def save_embeddings_to_db(df, batch_size=1000):
    update_sql = text("""
    UPDATE reviews
    SET embedding = :embedding
    WHERE review_id = :review_id
    """)
    with engine.connect() as conn:
        with conn.begin():
            for start in tqdm(range(0, len(df), batch_size), desc="Saving embeddings to DB"):
                batch = df.iloc[start:start+batch_size]
                params = batch[["review_id", "embedding"]].to_dict(orient="records")
                conn.execute(update_sql, params)

if __name__ == "__main__":
    reviews = get_unembedded_reviews()
    if reviews.empty:
        print("No new reviews to process.")
    else:
        reviews = generate_embeddings(reviews)
        save_embeddings_to_db(reviews)
        print("Embeddings updated.")


