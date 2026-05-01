from flask import Blueprint, request, jsonify, current_app
from app.database import get_db_connection

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Monitoring API is running"}), 200

@main.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@main.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, device_name, cpu_usage, memory_usage, disk_usage, status, timestamp
            FROM metrics
            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        metrics = []

        for row in rows:
            metrics.append({
                "id": row[0],
                "device_name": row[1],
                "cpu_usage": row[2],
                "memory_usage": row[3],
                "disk_usage": row[4],
                "status": row[5],
                "timestamp": row[6].isoformat() if row[6] else None
            })

        return jsonify(metrics), 200

    except Exception as e:
        current_app.logger.error(f"GET /metrics error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@main.route("/metrics", methods=["POST"])
def add_metric():
    try:
        data = request.get_json(silent=True)
        current_app.logger.info(f"POST /metrics called with data: {data}")

        if not data:
            current_app.logger.warning("POST /metrics failed: no JSON data received")
            return jsonify({"error": "No JSON data received"}), 400

        required_fields = [
            "device_name",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "status"
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            current_app.logger.warning(f"POST /metrics failed: missing fields {missing_fields}")
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO metrics (device_name, cpu_usage, memory_usage, disk_usage, status)
            OUTPUT INSERTED.id, INSERTED.timestamp
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["device_name"],
            data["cpu_usage"],
            data["memory_usage"],
            data["disk_usage"],
            data["status"]
        ))

        inserted_row = cursor.fetchone()

        conn.commit()
        conn.close()

        new_id = inserted_row[0]
        timestamp = inserted_row[1].isoformat() if inserted_row[1] else None

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