import json
import csv

# 输入和输出文件路径
input_file_path = "code/yelp_academic_dataset_business.json"
output_csv_path = "data/auto_repair_businesses_PA_filtered.csv"

# 过滤后的数据存储列表
filtered_data = []

# 要保留的CSV列名
csv_columns = [
    "business_id", "name","state","city","postal_code", "latitude", 
    "longitude", "stars", "review_count"
]

# 读取JSON文件并过滤数据
with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        business = json.loads(line.strip())
        
        
        if (
            "categories" in business and business["categories"] and 
            "Auto Repair" in business["categories"] and
            business.get("state", "") == "PA"
        ):
            filtered_business = {key: business.get(key, "") for key in csv_columns}
            filtered_data.append(filtered_business)


with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()
    writer.writerows(filtered_data)



