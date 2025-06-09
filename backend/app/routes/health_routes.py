from flask import Blueprint, jsonify, current_app
from ..extensions import mongo
from datetime import datetime
import os


health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/", methods=["GET"])
def root():
    """Ruta raíz para verificar que el servidor está funcionando"""
    return jsonify({
        "message": "DonaCrypto API v1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }), 200

@health_bp.route("/health", methods=["GET"])
def health_check():
    try:
        # Verificar conexión MongoDB
        mongo.db.command('ping')
        db_status = {
            "status": "connected",
            "database": mongo.db.name
        }
    except Exception as e:
        db_status = {
            "status": "error",
            "message": str(e)
        }
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }), 200


@health_bp.route("/debug", methods=["GET"])
def debug_info():
    return jsonify({
        "mongo_uri_configured": bool(current_app.config.get("MONGO_URI")),
        "mongo_db_name": current_app.config.get("MONGODB_DB"),
        "environment": os.getenv("FLASK_ENV"),
        "mongo_client_exists": bool(mongo.cx),
        "timestamp": datetime.now().isoformat()
    })