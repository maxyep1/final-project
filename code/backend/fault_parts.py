import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()  

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_db_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def extract_parts_from_best_business(best_business_str):
    """
    Parse the failure list from the best_business field
    """
    if not best_business_str:
        return []
    
    parts = best_business_str.split(",")
    cleaned_parts = []
    for p in parts:
        p = p.strip()
        if p.lower() == "unknown":
            continue
        if p:
            cleaned_parts.append(p)
    return cleaned_parts

def main():
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT best_business FROM business;")
    rows = cur.fetchall()

    all_parts = set()

    for r in rows:
        best_business_str = r['best_business']
        parts = extract_parts_from_best_business(best_business_str)
        for part in parts:
            all_parts.add(part)

    for part in all_parts:
        try:
            cur.execute("INSERT INTO fault_parts (part_name) VALUES (%s) ON CONFLICT (part_name) DO NOTHING;", (part,))
        except Exception as e:
            print(f"Error inserting part {part}: {e}")

    conn.commit()
    cur.close()
    conn.close()

    print("The fault part list has been generated and inserted into the fault_parts table.")

if __name__ == "__main__":
    main()
