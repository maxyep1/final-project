import json
from database import client

input_file_path = "data/yelp_academic_dataset_business.json"
'''The file path for input data'''
columns = [

    "business_id", "name", "state", "city", "address","postal_code",
    "latitude", "longitude", "stars", "review_count"
]


table_name = "business"

filtered_data = []
'''A list to store filtered data'''
with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        business = json.loads(line.strip())
        if (
            "categories" in business and business["categories"] and 
            "Auto Repair" in business["categories"] and
            business.get("state", "") == "PA"
        ):
            filtered_business = {key: business.get(key, None) for key in columns}
            filtered_data.append(filtered_business)

try:
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        business_id VARCHAR PRIMARY KEY,
        name VARCHAR,
        state VARCHAR,
        city VARCHAR,
        address VARCHAR,
        postal_code VARCHAR,
        latitude FLOAT,
        longitude FLOAT,
        stars FLOAT,
        review_count INT
    );
    """
    client.cursor().execute(create_table_query)
    client.commit()
    
    insert_query = f"""
    INSERT INTO {table_name} ({", ".join(columns)})
    VALUES ({", ".join(["%s"] * len(columns))})
    ON CONFLICT (business_id) DO NOTHING;
    """
    for business in filtered_data:
        client.cursor().execute(insert_query, tuple(business.values()))
    
    '''commit changes'''
    client.commit()
    print(f"insert {len(filtered_data)} data to table {table_name}")
except Exception as e:
    print(f"fault: {e}")