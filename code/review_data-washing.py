import pandas as pd
import json
import psycopg2
from dotenv import load_dotenv
import os

# 打印当前工作目录
print("当前工作目录:", os.getcwd())

# 获取脚本目录并切换工作目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print("已切换工作目录:", os.getcwd())

# 从环境变量中获取数据库配置
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# 文件路径
business_id_file = "../data/auto_repair_businesses_PA_filtered.csv"
review_file = "../data/yelp_academic_dataset_review.json"

# 读取 business_id 文件
print("步骤 1：加载 business_id 文件...")
business_ids = pd.read_csv(business_id_file)["business_id"].tolist()
print(f"从 {business_id_file} 加载了 {len(business_ids)} 个 business_id。")

# 连接到 PostgreSQL 数据库
print("步骤 2：连接到 PostgreSQL 数据库...")
try:
    client = psycopg2.connect(**db_config)
    cursor = client.cursor()
    print("数据库连接成功。")
except Exception as e:
    print(f"连接数据库时出错：{e}")
    exit()

# 创建 reviews 表（如果尚未创建）
create_table_query = """
CREATE TABLE IF NOT EXISTS reviews (
    business_id VARCHAR(255),
    stars INTEGER,
    text TEXT,
    date DATE
);
"""
cursor.execute(create_table_query)
client.commit()

# 读取和过滤评论，然后插入到数据库中
print("步骤 3：过滤评论并插入数据库...")
try:
    with open(review_file, 'r') as f:
        total_lines = sum(1 for _ in open(review_file, 'r'))  # 计算总行数
        f.seek(0)  # 重置文件指针
        processed_lines = 0
        for line in f:
            review = json.loads(line)
            processed_lines += 1
            if review["business_id"] in business_ids:
                # 移除不需要的项
                for key in ["user_id", "review_id", "useful", "funny", "cool"]:
                    review.pop(key, None)
                # 准备插入的数据
                data = (
                    review["business_id"],
                    review["stars"],
                    review["text"],
                    review["date"]
                )
                insert_query = """
                    INSERT INTO reviews (business_id, stars, text, date)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, data)
            # 打印进度
            if processed_lines % 10000 == 0:
                print(f"已处理 {processed_lines}/{total_lines} 行...")
        client.commit()
        print("数据插入完成。")
except Exception as e:
    print(f"处理数据时出错：{e}")
    client.rollback()
finally:
    cursor.close()
    client.close()
    print("数据库连接已关闭。")
