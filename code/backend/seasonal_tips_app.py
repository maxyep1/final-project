from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': 'yelp',
    'user': 'postgres',
    'password': 'econ_finalproject',
    'host': '34.57.181.108',
    'port': '5432'
}

def get_db_connection():
    """Establish a database connection."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.route('/api/maintenance_tips', methods=['GET'])
def get_maintenance_tips():
    """Get maintenance tips for a specific season."""
    season = request.args.get('season')  # Retrieve the 'season' parameter from the request
    if not season:
        return jsonify({'error': 'Season parameter is required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Query the maintenance tips for the specified season
        cursor.execute(
            "SELECT part_name, failure_probability FROM maintenance_tips WHERE season = %s ORDER BY failure_probability DESC;",
            (season,)
        )
        tips = cursor.fetchall()
        conn.close()

        # Convert query results to JSON
        result = [{'part_name': row[0], 'failure_probability': row[1]} for row in tips]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
