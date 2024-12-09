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

@app.route('/api/recommend', methods=['GET'])
def recommend_businesses():
    """
    用户提供 fault_id 或 query_text，以及 user_lat, user_lon。
    当前阶段仅返回 business_ids 列表作为初步结果。未来可在此继续扩展距离和评分逻辑。
    """
    user_lat = request.args.get('user_lat', type=float)
    user_lon = request.args.get('user_lon', type=float)
    fault_id = request.args.get('fault_id', type=str)
    query_text = request.args.get('query_text', type=str)

    if (not fault_id or fault_id.strip() == "") and (not query_text or query_text.strip() == ""):
        return jsonify({"error": "Either fault_id or query_text must be provided"}), 400

    if user_lat is None or user_lon is None:
        return jsonify({"error": "user_lat and user_lon must be provided"}), 400

    conn = get_db_conn()
    try:
        if fault_id and fault_id.strip():
            business_ids = get_business_ids_by_fault(conn, fault_id.strip())
        else:
            business_ids = get_business_ids_by_similarity(conn, query_text.strip())

        # 目前仅返回business_ids，为下游或后续逻辑提供数据源
        return jsonify({"business_ids": business_ids})
    finally:
        conn.close()
#part 2 (GIS)
def get_business_details_with_location(conn, business_ids):
    """
    Retrieve the name, stars, and location information for given business_ids.
    """
    if not business_ids:
        return []

    query = """
        SELECT business_id, name, stars, latitude, longitude
        FROM business
        WHERE business_id = ANY(%s);
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (business_ids,))
    rows = cur.fetchall()
    cur.close()

    # Convert the results into a list of dictionaries containing name, stars, latitude, and longitude
    business_details = [
        {
            "business_id": row["business_id"],
            "name": row["name"],
            "stars": row["stars"],
            "latitude": row["latitude"],
            "longitude": row["longitude"]
        }
        for row in rows
    ]
    return business_details
@app.route('/api/recommend', methods=['GET'])
def recommend_businesses_with_map():
    """
    Further filter the recommended businesses to find the 7 nearest ones, 
    sort them by rating, and return detailed information, including labels for map display.
    """
    user_lat = request.args.get('user_lat', type=float)
    user_lon = request.args.get('user_lon', type=float)
    fault_id = request.args.get('fault_id', type=str)
    query_text = request.args.get('query_text', type=str)

    if (not fault_id or fault_id.strip() == "") and (not query_text or query_text.strip() == ""):
        return jsonify({"error": "Either fault_id or query_text must be provided."}), 400

    if user_lat is None or user_lon is None:
        return jsonify({"error": "Both user_lat and user_lon must be provided."}), 400

    conn = get_db_conn()
    try:
        # Retrieve business_ids based on fault_id or query_text
        if fault_id and fault_id.strip():
            business_ids = get_business_ids_by_fault(conn, fault_id.strip())
        else:
            business_ids = get_business_ids_by_similarity(conn, query_text.strip())

        # If no matching businesses are found
        if not business_ids:
            return jsonify({
                "businesses": [],
                "message": "Your search did not match any businesses. Try using our Fault Part search feature to find a suitable store."
            }), 404

        # Filter the 7 nearest businesses
        nearest_businesses = get_nearest_businesses(user_lat, user_lon, business_ids, conn)

        # Retrieve detailed information for businesses, including ratings and names
        business_ids_sorted = [b["business_id"] for b in nearest_businesses]
        business_details = get_business_details_with_location(conn, business_ids_sorted)

        # Sort businesses by rating in descending order
        sorted_businesses = sorted(business_details, key=lambda x: -x["stars"])
        for idx, business in enumerate(sorted_businesses):
            business["label"] = chr(65 + idx)  # Add labels A, B, C, ..., G


if __name__ == "__main__":
    app.run(debug=True)
