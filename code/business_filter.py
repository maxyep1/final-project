import json
from database import client
# 输入文件路径
input_file_path = "data/yelp_academic_dataset_business.json"
# 要保留的列名
columns = [
    "business_id", "name", "state", "city", "postal_code",
    "latitude", "longitude", "stars", "review_count"
]
# 要插入的表名
table_name = "business"
# 过滤后的数据存储列表
filtered_data = []
# 读取JSON文件并过滤数据
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
# 连接到数据库并插入数据
try:
    # 建立数据库连接
    
    # 创建表（如果不存在）
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        business_id VARCHAR PRIMARY KEY,
        name VARCHAR,
        state VARCHAR,
        city VARCHAR,
        postal_code VARCHAR,
        latitude FLOAT,
        longitude FLOAT,
        stars FLOAT,
        review_count INT
    );
    """
    client.cursor().execute(create_table_query)
    client.commit()
    # 插入数据
    insert_query = f"""
    INSERT INTO {table_name} ({", ".join(columns)})
    VALUES ({", ".join(["%s"] * len(columns))})
    ON CONFLICT (business_id) DO NOTHING;
    """
    for business in filtered_data:
        client.cursor().execute(insert_query, tuple(business.values()))
    
    # 提交更改
    client.commit()
    print(f"成功插入 {len(filtered_data)} 条数据到表 {table_name}")
except Exception as e:
    print(f"发生错误: {e}")