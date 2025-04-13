from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from ..extensions import mongo
from ..decorators.role_required import role_required
from ..models.user import User

creator_bp = Blueprint("creatoy_bp", __name__)

@creator_bp.route("/creators/<username>", methods=["GET"])
def public_creator_profile(username):
    """Perfil público solo de creadores"""
    try:
        user = mongo.db.users.find_one(
            {"username": username, "role": "creator"},
            {"_id": 0, "password": 0}
        )
        if not user:
            return jsonify({"error": "Creador no encontrado o no autorizado"}), 404

        # Estadísticas
        pipeline = [
            {"$match": {"receiver_email": user["email"]}},
            {
                "$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$amount"},
                    "total_count": {"$sum": 1}
                }
            }
        ]
        stats = list(mongo.db.donations.aggregate(pipeline))
        total_amount = stats[0]["total_amount"] if stats else 0
        total_count = stats[0]["total_count"] if stats else 0

        return jsonify({
            "username": user["username"],
            "bio": user.get("bio", ""),
            "avatar_url": user.get("avatar_url", ""),
            "total_donations_received": total_amount,
            "number_of_donations": total_count
        }), 200

    except Exception as e:
        current_app.logger.error(f"[public_creator_profile] Error: {e}")
        return jsonify({"error": "Error al obtener el perfil"}), 500
    

@creator_bp.route("/creators/dashboard", methods=["GET"])
@jwt_required()
@role_required("creator")
def creator_dashboard():
    """Panel del creador: ver donaciones y estadísticas"""
    try:
        email = get_jwt_identity()

        # Obtener donaciones recibidas
        donations = list(mongo.db.donations.find(
            {"receiver_email": email},
            {"_id": 0}
        ))

        # Calcular estadísticas
        total_amount = sum(d["amount"] for d in donations)
        total_donations = len(donations)

        # Incluir:
        # - Número de seguidores
        # - Likes en posts, etc.

        return jsonify({
            "donations": donations,
            "total_donations": total_donations,
            "total_received": total_amount
        }), 200

    except Exception as e:
        current_app.logger.error(f"[creator_dashboard] Error: {e}")
        return jsonify({"error": "Error al obtener el panel del creador"}), 500
    

@creator_bp.route("/creators/update-profile", methods=["PUT"])
@jwt_required()
@role_required("creator")
def update_creator_profile():
    """Actualizar perfil del creador"""
    try:
        email = get_jwt_identity()
        data = request.get_json()
        allowed_fields = ["bio", "avatar_url", "username", "email"]

        update_data = { k: v for k, v in data.items() if k in allowed_fields}
        if not update_data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
        
        # Verificar si el email ya existe
        if "email" in update_data:
            existing = mongo.db.users.find_one({"email": update_data["email"]}, {"email": {"$ne": email}})
            if existing:
                return jsonify({"error": "El email ya está en uso"}), 409
            
        # Actualizar email en DB
        mongo.db.users.update_one(
            {"email": email},
            {"$set": update_data})
        return jsonify({"message": "Perfil actualizado con éxito"})

    except Exception as e:
        current_app.logger.error("update_creator_profile] Error: ".format())
        return jsonify({"error": "Error al actualizar el perfil"}), 500

@creator_bp.route("/creators/create-post", methods=["POST"])
@jwt_required()
@role_required("creator")
def create_post():
    """Crear un nuevo post en el perfil del creador"""
    try:
        email = get_jwt_identity()
        data = request.get_json()

        required_fields = ["title", "content"]
        if not data and  not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos requeridos"}), 400

        post= {
            "title": data["title"],
            "content": data["content"],
            "creator_email": email,
            "created_at": datetime.utcnow()
        }

        # Guardar el post en la base de datos
        mongo.db.posts.insert_one(post)
        return jsonify({"message": "Post creado con éxito"}), 201	

    except Exception as e:
        current_app.logger.error("[create_post] Error: {}".format(e))
        return jsonify({"error": "Error al crear el post"}), 500
    
@creator_bp.route("/creators/posts/<username>", methods=["GET"])
def get_creator_posts(username):
    """Obtener posts de un creador por su username"""
    try:
        # Paginación
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit

        # Obtener email del creador
        creator = mongo.db.users.find_one({"username": username}, {"role": "creator"})
        if not creator:
            return jsonify({"error": "Creador no encontrado"}), 404
        email = creator["email"]

        # Total posts
        total_posts = mongo.db.posts.count_documents({"creator_email": email})

        # Obtener posts del creador
        # Aplica paginación con skip (cuántos documentos saltar) y limit (cuántos traer).
        posts_cursor = mongo.db.posts.find({"author_email": email}).sort("created_at", -1).skip(skip).limit(limit)
        # Convertir el cursor en una lista de diccionarios y transformamos el campo _id (ObjectId) a string
        posts = [{**post, "_id": str(post["_id"])} for post in posts_cursor]
        
        return jsonify({
            "posts": posts,
            "page": page,
            "limit": limit,
            "total": total_posts,
            "pages": (total_posts + limit - 1) // limit            
            }), 200
    
    except Exception as e:
        current_app.logger.error("[get_creator_posts] Error: {}".format(e))
        return jsonify({"error": "Error al obtener los posts del creador"}), 500

@creator_bp.route("/creators/delete-post/<post_id>", methods=["DELETE"])
@jwt_required()
@role_required("creator")
def delete_post(post_id):
    """Eliminar un post del creador"""
    try:
        email = get_jwt_identity()

        # Verificar que el post existe y pertenence al creador
        post = mongo.db.posts.find_one({"_id": ObjectId(post_id)}, {"creator_email": email})
        if not post:
            return jsonify({"error": "Post no encontrado o no  autoriado"}), 404
        
        # Eliminar post
        mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
        return jsonify({"message": "Post eliminado"}), 200
    except Exception as e:
        current_app.logger.error("[deletel_post] error: {}".format(e))
        return jsonify({"error": "Error al elimianr post"}), 500
    
# Probar sistema de posts y modificación de perfil de creador
