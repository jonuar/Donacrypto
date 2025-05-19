from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.donation import Donation
from ..extensions import mongo
from dotenv import load_dotenv
import os
import requests

load_dotenv()

donation_bp = Blueprint("donation_bp", __name__)

COINDROP_API_KEY = os.gentenv('COINDROP_API_URL', 'https://api.coindrop.io/v1')
COINDROP_API_URL = os.getenv("COINDROP_API_KEY", 'API_KEY')

@donation_bp.route("/donate", methods=["POST"])
@jwt_required()
def donate():
    '''Procesa y registra una donación'''
    try:
        # Validación de datos de entrada
        data = request.get_json()
        required_fields = ("receiver_email", "amount")
        if not data or not all(f in data for f in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        # Validar cantidad
        if data["amount"] <= 0:
            return jsonify({"error": "Cantidad no válida"}), 400

        # Obtener email (JWT) del usuario que hace la donación y demás datos
        sender_email = get_jwt_identity()
        amount = data["amount"]
        receiver_email = data["reveiver_email"]

        # Calcular comisión (10% para la plataforma y 90% para el creador)
        platform_fee = round(amount * 0.10, 2)
        creator_amount = round(amount * 0.90, 2)

        # Prepara payload para la solicitud a Coindrop
        payload = {
            "amount": amount,
            "currency": data.get("currency", "ETH"),
            "metadata": {
                "sender_email": sender_email,
                "receiver_email": receiver_email,
                "platform_fee": platform_fee,
                "creator_amount": creator_amount,
            }
            # Agregar otros parámetros requeridos por la API de Coindrop si es necesario
        }

        # Headers para autenticación y tipo de contenido
        headers = {
            "Autorization": "Bearer {}".format(COINDROP_API_KEY),
            "Content-Type": "application/json"
        }

        # Realiza la solicitud a la API de Coindrop
        response = request.post("{}/payments".format(COINDROP_API_URL), json=payload, headers=headers)
        response.raise_for_status() # Lanza un error si la respuesta no es 200
        payment_data = response.json() # Se espera un 'tx_hash' que identifique la transacción

        # Registrar donación en la base de datos
        donation = Donation(
            sender_email=sender_email,
            receiver_email=receiver_email,
            amount=amount,
            tx_hash=payment_data["tx_hash"], # tx_hash devuelto por Coindrop
            currency=data.get("currency", "ETH")
        )

        if donation.save_to_db():
            return jsonify({"message": "Donación registrada con éxito",
                            "payment_data": payment_data
                    }), 201
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
        total = mongo.db.donations.count_documents({"receiver_email": user_email})

        return jsonify({
                    "donations": list(donations),
                    "total": total,
                    "page": page,
                    "limit": limit,
                }), 200
    except Exception as e:
        current_app.logger.error(f"[get_received_donations] Error: {e}")
        return jsonify({"error": "Error al obtener historial de donaciones"}), 500
