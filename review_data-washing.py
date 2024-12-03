import pandas as pd
import json

# 文件路径
business_id_file = "/Users/fan/Downloads/auto_repair_businesses_PA_filtered.csv"
review_file = "/Users/fan/Downloads/yelp_academic_dataset_review.json"
output_file = "/Users/fan/Downloads/filtered_reviews.json"

# 读取 business_id 文件
print("Step 1: Loading business_id file...")
business_ids = pd.read_csv(business_id_file)["business_id"].tolist()
print(f"Loaded {len(business_ids)} business_ids from {business_id_file}.")

# 创建存储筛选结果的列表
filtered_reviews = []

# 逐行读取 JSON 文件，筛选符合条件的 review
print("Step 2: Filtering reviews based on business_id...")
with open(review_file, 'r') as f:
    total_lines = sum(1 for _ in open(review_file, 'r'))  # 计算总行数
    processed_lines = 0
    for line in f:
        review = json.loads(line)  # 解析 JSON 行
        processed_lines += 1
        if review["business_id"] in business_ids:
            # 移除不需要的项
            for key in ["user_id", "review_id", "useful", "funny", "cool"]:
                review.pop(key, None)
            filtered_reviews.append(review)
        # 打印进度
        if processed_lines % 10000 == 0:
            print(f"Processed {processed_lines}/{total_lines} lines...")

print(f"Filtering completed. Total reviews matched: {len(filtered_reviews)}")

# 将筛选结果保存为新的 JSON 文件
print("Step 3: Saving filtered reviews to output file...")
with open(output_file, 'w') as f:
    for review in filtered_reviews:
        f.write(json.dumps(review) + "\n")

print(f"Filtered reviews saved to {output_file}.")