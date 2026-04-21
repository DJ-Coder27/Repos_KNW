from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.database import get_db_connection, init_db

main = Blueprint("main", __name__)

init_db()

@main.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Monitoring API is running"}), 200

@main.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@main.route("/metrics", methods=["GET"])
def get_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metrics")
    rows = cursor.fetchall()
    conn.close()

    metrics = [dict(row) for row in rows]
    return jsonify(metrics), 200

@main.route("/metrics", methods=["POST"])
def add_metric():
    try:
        data = request.get_json()
        current_app.logger.info(f"POST /metrics called with data: {data}")

        if not data:
            current_app.logger.warning("POST /metrics failed: no JSON data received")
            return jsonify({"error": "No JSON data received"}), 400

        required_fields = ["device_name", "cpu_usage", "memory_usage", "disk_usage", "status"]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            current_app.logger.warning(f"POST /metrics failed: missing fields {missing_fields}")
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        timestamp = datetime.utcnow().isoformat()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO metrics (device_name, cpu_usage, memory_usage, disk_usage, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["device_name"],
            data["cpu_usage"],
            data["memory_usage"],
            data["disk_usage"],
            data["status"],
            timestamp
        ))

        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        current_app.logger.info(f"Metric stored successfully for device: {data['device_name']}")

        return jsonify({
            "id": new_id,
            "device_name": data["device_name"],
            "cpu_usage": data["cpu_usage"],
            "memory_usage": data["memory_usage"],
            "disk_usage": data["disk_usage"],
            "status": data["status"],
            "timestamp": timestamp
        }), 201

    except Exception as e:
        current_app.logger.error(f"POST /metrics error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500