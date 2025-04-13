from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.donation import Donation
from ..extensions import mongo

donation_bp = Blueprint("donation_bp", __name__)


@donation_bp.route("/donate", methods=["POST"])
@jwt_required()
def donate():
    try:
        data = request.get_json()
        required_fields = ("receiver_email", "amount", "tx_hash")
        if not data or not all(f in data for f in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        # Validar cantidad
        if data["amount"] <= 0:
            return jsonify({"error": "Cantidad no válida"}), 400

        sender_email = (
            get_jwt_identity()
        )  # Obtener el email del usuario actual (token JWT)

        donation = Donation(
            sender_email=sender_email,
            receiver_email=data["receiver_email"],
            amount=data["amount"],
            tx_hash=data["tx_hash"],
            currency=data.get("currency", "ETH"),
        )

        if donation.save_to_db():
            return jsonify({"message": "Donación registrada con éxito"}), 201
        else:
            return jsonify({"error": "Error al guardar donación"}), 500

    except Exception as e:
        current_app.logger.error(f"[donate] Error: {e}")
        return jsonify({"error": "Error interno"}), 500


@donation_bp.route("/sent", methods=["GET"])
@jwt_required()
def get_sent_donations():
    """Devuelve las donaciones enviadas por el usuario autenticado"""
    try:
        user_email = get_jwt_identity()

        # Paginación
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit

        # Orden por fecha descendente
        donations = (
            mongo.db.donations.find(
                {"sender_email": user_email}, {"_id": 0, "sender_email": 1, "amount": 1}
            )
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        # Total de donaciones enviadas
        total = mongo.db.donations.count_documents({"sender_email": user_email})

        return jsonify({
                    "donations": list(donations),
                    "total": total,
                    "page": page,
                    "limit": limit,
                }), 200        
    except Exception as e:
        current_app.logger.error(f"[get_sent_donations] Error: {e}")
        return jsonify({"error": "Error al obtener historial de donaciones"}), 500


@donation_bp.route("/received", methods=["GET"])
@jwt_required()
def get_received_donations():
    """Devuelve las donaciones recibidas por el usuario autenticado"""
    try:
        user_email = get_jwt_identity()

        # Parámetros de paginación
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit

        # Consulta ordenada por fecha descendente
        donations = (
            mongo.db.donations.find(
                {"receiver_email": user_email},
                {"_id": 0, "receiver_email": 1, "amount": 1},
            )
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Total de donaciones recibidas
        total = mongo.db.donations.count_documents({"sender_email": user_email})

        return jsonify({
                    "donations": list(donations),
                    "total": total,
                    "page": page,
                    "limit": limit,
                }), 200
    except Exception as e:
        current_app.logger.error(f"[get_received_donations] Error: {e}")
        return jsonify({"error": "Error al obtener historial de donaciones"}), 500
