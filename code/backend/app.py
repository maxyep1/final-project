import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

model = SentenceTransformer('all-MiniLM-L6-v2')

app = Flask(__name__)

def get_db_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/api/fault-parts', methods=['GET'])
def get_fault_parts():
    """
    返回故障部位列表给前端，用于生成下拉菜单。
    """
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT part_name FROM fault_parts ORDER BY part_name;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    parts = [r['part_name'] for r in rows] if rows else []
    return jsonify({"fault_parts": parts})

def get_business_ids_by_fault(conn, fault_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT business_id
        FROM business
        WHERE best_business = %s
    """, (fault_id,))
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows] if rows else []

def get_business_ids_by_similarity(conn, query_text):
    user_vec = model.encode(query_text)
    user_vec_str = "[" + ",".join(str(x) for x in user_vec) + "]"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT business_id
        FROM reviews
        ORDER BY embedding <-> %s
        LIMIT 100;
    """, (user_vec_str,))
    rows = cur.fetchall()
    cur.close()
    if not rows:
        return []
    biz_ids = {r['business_id'] for r in rows}
    return list(biz_ids)

def get_business_details_with_location(conn, business_ids):
    """
    根据 business_ids 查询店铺的详细信息，包括名称、评分、地址和地理数据（geom）。
    假设 business表中有 name, stars, address, geom 字段，geom是地理字段（geometry/geography）。
    """
    if not business_ids:
        return []
    query = """
        SELECT name, stars, address, ST_AsGeoJSON(geom) AS geom
        FROM business
        WHERE business_id = ANY(%s);
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (business_ids,))
    rows = cur.fetchall()
    cur.close()
    business_details = [
        {
            "name": row["name"],
            "stars": row["stars"],
            "address": row["address"],
            "geom": row["geom"]
        }
        for row in rows
    ]
    return business_details

@app.route('/api/recommend', methods=['GET'])
def recommend_businesses():
    """
    最终推荐接口：
    - 用户提供 fault_id 或 query_text，以及 user_lat, user_lon。
    - 根据参数获得 business_ids。
    - 如果有坐标，用PostGIS计算最近7家店，并按评分排序。
    - 没有坐标则只按评分取前7家。
    """
    user_lat = request.args.get('user_lat', type=float)
    user_lon = request.args.get('user_lon', type=float)
    fault_id = request.args.get('fault_id', type=str)
    query_text = request.args.get('query_text', type=str)

    if (not fault_id or fault_id.strip() == "") and (not query_text or query_text.strip() == ""):
        return jsonify({"error": "Either fault_id or query_text must be provided"}), 400

    conn = get_db_conn()
    try:
        # 获取business_ids
        if fault_id and fault_id.strip():
            business_ids = get_business_ids_by_fault(conn, fault_id.strip())
        else:
            business_ids = get_business_ids_by_similarity(conn, query_text.strip())

        if not business_ids:
            return jsonify({
                "businesses": [],
                "message": "No matching businesses found. Please try another fault part or description."
            }), 404

        if user_lat is not None and user_lon is not None:
            # 使用PostGIS计算最近店铺
            nearest_query = """
                SELECT name, stars, address, ST_AsGeoJSON(geom) AS geom,
                       ST_Distance(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) AS distance
                FROM business
                WHERE business_id = ANY(%s)
                ORDER BY distance ASC
                LIMIT 7;
            """
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(nearest_query, (user_lon, user_lat, business_ids))
            rows = cur.fetchall()
            cur.close()

            nearest_businesses = [
                {
                    "name": row["name"],
                    "stars": row["stars"],
                    "address": row["address"],
                    "geom": row["geom"],
                    "distance": row["distance"]
                }
                for row in rows
            ]

            # 按评分排序（评分降序）
            sorted_businesses = sorted(nearest_businesses, key=lambda x: -x["stars"])
        else:
            # 无坐标则仅按评分排序前7家
            business_details = get_business_details_with_location(conn, business_ids)
            sorted_businesses = sorted(business_details, key=lambda x: -x["stars"])[:7]

        result = {
            "businesses": [
                {
                    "name": b["name"],
                    "stars": b["stars"],
                    "address": b["address"],
                    "geom": b["geom"]
                }
                for b in sorted_businesses
            ]
        }

        return jsonify(result)
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)