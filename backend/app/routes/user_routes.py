from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from bson import ObjectId

from ..decorators.role_required import role_required
from ..models.post import Post
from ..models.user import User
from ..models.following import Following
from ..models.creator_wallet import CreatorWallet
from ..models.like import Like
from ..utils.like_utils import add_like_info_to_posts
from ..extensions import mongo

user_bp = Blueprint("user_bp", __name__)

# FUNCIONES AUXILIARES

def convert_bson_dates_to_iso(data):
    """Convierte fechas BSON de MongoDB a strings ISO para JSON"""
    if isinstance(data, dict):
        if "$date" in data:
            # Es una fecha BSON, convertir a ISO string
            return data["$date"]
        else:
            # Es un diccionario normal, procesar recursivamente
            return {key: convert_bson_dates_to_iso(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Es una lista, procesar cada elemento
        return [convert_bson_dates_to_iso(item) for item in data]
    elif isinstance(data, datetime):
        # Es un objeto datetime de Python
        return data.isoformat() + "Z"
    else:
        # Es un valor primitivo, retornar tal como está
        return data

def process_post_for_json(post_dict):
    """Procesa un post para serialización JSON correcta"""
    # Convertir ObjectId a string
    post_dict["_id"] = str(post_dict["_id"])
    
    # Convertir fechas BSON a ISO strings
    post_dict = convert_bson_dates_to_iso(post_dict)
    
    return post_dict

def find_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario por su correo electrónico en la base de datos
    
    Args:
        email: El correo electrónico a buscar
        
    Returns:
        Un diccionario con los datos del usuario si se encuentra, None en caso contrario
    """
    try:
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            return user_data
        return None
    except Exception as e:
        current_app.logger.error(f"[find_by_email] Error: {e}")
        return None 

# RUTAS COMUNES PARA TODOS LOS USUARIOS

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile() -> Tuple[Any, int]:
    """
    Obtiene el perfil completo del usuario autenticado
    
    Requiere: JWT válido en cabecera
    Retorna: datos completos del perfil del usuario
    """
    try:
        email: str = get_jwt_identity()
        user_data: Optional[Dict[str, Any]] = find_by_email(email)
        
        if not user_data:
            return jsonify({"error": "Usuario no encontrado"}), 404
          # Excluir información sensible
        if "password" in user_data:
            del user_data["password"]
        if "_id" in user_data:
            user_data["_id"] = str(user_data["_id"])
            
        # Convertir fechas BSON a formato JSON
        user_data = convert_bson_dates_to_iso(user_data)
            
        return jsonify(user_data), 200
    except Exception as e:
        current_app.logger.error(f"[get_user_profile] Error: {e}")
        return jsonify({"error": "Error al obtener el perfil"}), 500


@user_bp.route("/update-profile", methods=["PUT"])
@jwt_required()
def update_user_profile() -> Tuple[Any, int]:
    """
    Actualiza el perfil del usuario autenticado
    
    Requiere: JWT válido en cabecera
    Campos permitidos: username, bio, avatar_url
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()
        
        # Campos permitidos para actualizar (excluimos email y password que tienen rutas específicas)
        allowed_fields: List[str] = ["username", "bio", "avatar_url"]
        update_data: Dict[str, Any] = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({"error": "No se proporcionaron datos válidos para actualizar"}), 400
            
        # Verificar si el username ya existe (para otro usuario)
        if "username" in update_data:
            existing = mongo.db.users.find_one({"username": update_data["username"], "email": {"$ne": email}})
            if existing:
                return jsonify({"error": "El nombre de usuario ya está en uso"}), 409
                
        # Actualizar perfil
        result = mongo.db.users.update_one(
            {"email": email},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({"message": "Perfil actualizado con éxito"}), 200
        else:
            return jsonify({"message": "No se realizaron cambios"}), 200
            
    except Exception as e:
        current_app.logger.error(f"[update_user_profile] Error: {e}")
        return jsonify({"error": "Error al actualizar el perfil"}), 500


@user_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password() -> Tuple[Any, int]:
    """
    Cambia la contraseña del usuario autenticado
    
    Requiere: JWT válido en cabecera, current_password, new_password
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()
        
        if not data or "current_password" not in data or "new_password" not in data:
            return jsonify({"error": "Se requiere contraseña actual y nueva"}), 400
            
        # Verificar contraseña actual
        from ..models.user import User
        user_data = find_by_email(email)
        if not user_data:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        user = User.from_dict(user_data)
        if not user.check_password(data["current_password"]):
            return jsonify({"error": "Contraseña actual incorrecta"}), 401
            
        # Cambiar contraseña
        hashed_password: str = generate_password_hash(data["new_password"])
        mongo.db.users.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )
        
        return jsonify({"message": "Contraseña actualizada con éxito"}), 200
    except Exception as e:
        current_app.logger.error(f"[change_password] Error: {e}")
        return jsonify({"error": "Error al cambiar la contraseña"}), 500
        
        
@user_bp.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account() -> Tuple[Any, int]:
    """
    Elimina la cuenta del usuario autenticado
    
    Requiere: JWT válido en cabecera, password para confirmar
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()
        
        if not data or "password" not in data:
            return jsonify({"error": "Se requiere contraseña para confirmar"}), 400
            
        # Verificar contraseña
        from ..models.user import User
        user_data = find_by_email(email)
        if not user_data:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        user = User.from_dict(user_data)
        if not user.check_password(data["password"]):
            return jsonify({"error": "Contraseña incorrecta"}), 401
            
        # Eliminar cuenta y datos relacionados
        # En un sistema real, esto podría implicar eliminar datos asociados, tokens, etc.
        result = mongo.db.users.delete_one({"email": email})
        
        if result.deleted_count > 0:
            # También sería bueno invalidar el token JWT actual
            jti: str = get_jwt()["jti"]
            from ..extensions import blacklist
            blacklist.add(jti)
            
            return jsonify({"message": "Cuenta eliminada con éxito"}), 200
        else:
            return jsonify({"error": "No se pudo eliminar la cuenta"}), 500
            
    except Exception as e:
        current_app.logger.error(f"[delete_account] Error: {e}")
        return jsonify({"error": "Error al eliminar la cuenta"}), 500


# RUTAS PARA FOLLOWERS

@user_bp.route("/feed", methods=["GET"])
@role_required("follower")
def follower_feed() -> Tuple[Any, int]:
    """
    Obtiene el feed personalizado del follower con posts de creadores seguidos
    
    Requiere: JWT válido en cabecera
    Retorna: lista de publicaciones de creadores seguidos
    """
    try:
        email: str = get_jwt_identity()
        
        # Paginación
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 10))
        skip: int = (page - 1) * limit
        
        # Obtener lista de creadores seguidos
        following_data = mongo.db.followings.find(
            {"follower_email": email},
            {"_id": 0, "creator_email": 1}
        )
        
        creator_emails: List[str] = [item["creator_email"] for item in following_data]
        
        if not creator_emails:
            return jsonify({
                "posts": [],
                "message": "No sigues a ningún creador. ¡Explora y sigue a algunos creadores!",
                "page": page,            "pages": 0,
                "total": 0
            }), 200
        
        # Obtener posts de los creadores seguidos
        total_posts = mongo.db.posts.count_documents({"creator_email": {"$in": creator_emails}})
        posts_cursor = mongo.db.posts.find({"creator_email": {"$in": creator_emails}}) \
                      .sort("created_at", -1) \
                      .skip(skip) \
                      .limit(limit)
        posts: List[Dict[str, Any]] = []
        for post in posts_cursor:
            # Convertir fechas y ObjectId para JSON
            post_dict = dict(post)
            post_dict = process_post_for_json(post_dict)
            
            # Obtener información básica del creador
            creator = mongo.db.users.find_one(
                {"email": post_dict["creator_email"]},
                {"_id": 0, "username": 1, "avatar_url": 1}
            )
            
            if creator:
                post_dict["creator_username"] = creator["username"]
                post_dict["creator_avatar"] = creator.get("avatar_url", "")
                
            posts.append(post_dict)
        
        # Agregar información de likes usando la función utilitaria
        follower_email = get_jwt_identity()
        posts = add_like_info_to_posts(posts, follower_email)
            
        return jsonify({
            "posts": posts,
            "page": page,
            "limit": limit,
            "total": total_posts,
            "pages": (total_posts + limit - 1) // limit
        }), 200
    except Exception as e:
        current_app.logger.error(f"[follower_feed] Error: {e}")
        return jsonify({"error": "Error al obtener el feed"}), 500


@user_bp.route("/search-creators", methods=["GET"])
@role_required("follower")
def search_creators() -> Tuple[Any, int]:
    """
    Busca creadores por username para que los followers puedan seguirlos
    
    Requiere: JWT válido en cabecera, rol follower
    Query params: q (search query), page, limit
    Retorna: lista de creadores que coinciden con la búsqueda
    """
    try:
        follower_email: str = get_jwt_identity()
        
        # Parámetros de búsqueda
        search_query: str = request.args.get("q", "").strip()
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 10))
        skip: int = (page - 1) * limit
        
        if not search_query:
            return jsonify({
                "creators": [],
                "message": "Proporciona un término de búsqueda",
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }), 200
        
        # Validar longitud mínima
        if len(search_query) < 2:
            return jsonify({
                "creators": [],
                "message": "El término de búsqueda debe tener al menos 2 caracteres",
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }), 200
        
        # Crear query de búsqueda (case insensitive)
        search_pattern = {"$regex": search_query, "$options": "i"}
        query = {
            "role": "creator",
            "$or": [
                {"username": search_pattern},
                {"bio": search_pattern}
            ]
        }
        
        # Contar total de resultados
        total_creators = mongo.db.users.count_documents(query)
        
        # Realizar búsqueda con paginación
        creators_cursor = mongo.db.users.find(
            query,
            {"_id": 0, "password": 0, "email": 0}  # Excluir información sensible
        ).sort("username", 1).skip(skip).limit(limit)
        
        creators: List[Dict[str, Any]] = []
        
        # Obtener lista de creadores que ya sigue este follower
        following_data = mongo.db.followings.find(
            {"follower_email": follower_email},
            {"_id": 0, "creator_email": 1}
        )
        followed_emails = {item["creator_email"] for item in following_data}
        
        for creator in creators_cursor:
            # Añadir información adicional
            creator_email = creator.get("email", "")
            
            # Número de seguidores
            followers_count = mongo.db.followings.count_documents({"creator_email": creator_email})
            creator["followers_count"] = followers_count
            
            # Número de posts
            posts_count = mongo.db.posts.count_documents({"creator_email": creator_email})
            creator["posts_count"] = posts_count
            
            # Si ya lo sigue
            creator["following"] = creator_email in followed_emails
            
            creators.append(creator)
        
        return jsonify({
            "creators": creators,
            "page": page,
            "limit": limit,
            "total": total_creators,
            "pages": (total_creators + limit - 1) // limit,
            "query": search_query,
            "message": f"Se encontraron {total_creators} creadores para '{search_query}'"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[search_creators] Error: {e}")
        return jsonify({"error": "Error al buscar creadores"}), 500

@user_bp.route("/explore-all-creators", methods=["GET"])
@role_required("follower")
def explore_all_creators() -> Tuple[Any, int]:
    """
    Explora todos los creadores disponibles (no solo los seguidos)
    
    Requiere: JWT válido en cabecera, rol follower
    Query params: page, limit, sort (popular, recent, alphabetical)
    Retorna: lista paginada de todos los creadores
    """
    try:
        follower_email: str = get_jwt_identity()
        
        # Paginación
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 12))
        skip: int = (page - 1) * limit
        
        # Ordenación
        sort_by: str = request.args.get("sort", "popular")
        
        # Query base para todos los creadores
        query = {"role": "creator"}
        
        # Contar total de creadores
        total_creators = mongo.db.users.count_documents(query)
        
        if sort_by == "alphabetical":
            sort_criteria = [("username", 1)]
        elif sort_by == "recent":
            sort_criteria = [("created_at", -1)]
        else:  # popular (por defecto)
            sort_criteria = [("username", 1)]  # Temporal, ordenaremos después
        
        # Obtener creadores
        creators_cursor = mongo.db.users.find(
            query,
            {"_id": 0, "password": 0}
        ).sort(sort_criteria).skip(skip).limit(limit)
        
        creators: List[Dict[str, Any]] = []
        
        # Obtener lista de creadores que ya sigue
        following_data = mongo.db.followings.find(
            {"follower_email": follower_email},
            {"_id": 0, "creator_email": 1}
        )
        followed_emails = {item["creator_email"] for item in following_data}
        
        for creator in creators_cursor:
            # Información adicional
            creator_email = creator["email"]
            
            # Número de seguidores
            followers_count = mongo.db.followings.count_documents({"creator_email": creator_email})
            creator["followers_count"] = followers_count
            
            # Número de posts
            posts_count = mongo.db.posts.count_documents({"creator_email": creator_email})
            creator["posts_count"] = posts_count
            
            # Si ya lo sigue
            creator["following"] = creator_email in followed_emails
            
            # Eliminar email por seguridad
            del creator["email"]
            
            creators.append(creator)
        
        # Ordenar por popularidad si se solicitó
        if sort_by == "popular":
            creators.sort(key=lambda x: x["followers_count"], reverse=True)
        
        return jsonify({
            "creators": creators,
            "page": page,
            "limit": limit,
            "total": total_creators,
            "pages": (total_creators + limit - 1) // limit,
            "sort": sort_by,
            "message": f"Mostrando {len(creators)} de {total_creators} creadores disponibles"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[explore_all_creators] Error: {e}")
        return jsonify({"error": "Error al explorar creadores"}), 500


@user_bp.route("/following", methods=["GET"])
@role_required("follower")
def get_following() -> Tuple[Any, int]:
    """
    Obtiene la lista de creadores que sigue el usuario
    
    Requiere: JWT válido en cabecera
    Retorna: lista de creadores seguidos
    """
    try:
        email: str = get_jwt_identity()
        
        # Busca en la colección de seguimientos los creadores que sigue este usuario
        following_data = mongo.db.followings.find(
            {"follower_email": email},
            {"_id": 0, "creator_email": 1, "created_at": 1}
        )
        
        # Extrae la lista de emails de creadores
        creator_emails: List[str] = [item["creator_email"] for item in following_data]
        
        if not creator_emails:
            return jsonify({"following": [], "count": 0}), 200
            
        # Busca los datos de los creadores
        creators: List[Dict[str, Any]] = []
        for creator_email in creator_emails:
            creator_data = mongo.db.users.find_one(
                {"email": creator_email, "role": "creator"},
                {"_id": 0, "username": 1, "email": 1, "avatar_url": 1, "bio": 1}
            )
            if creator_data:
                creators.append(creator_data)
        
        return jsonify({"following": creators, "count": len(creators)}), 200
    except Exception as e:
        current_app.logger.error(f"[get_following] Error: {e}")
        return jsonify({"error": "Error al obtener los creadores seguidos"}), 500


@user_bp.route("/follow", methods=["POST"])
@role_required("follower")
def follow_creator() -> Tuple[Any, int]:
    """
    Sigue a un nuevo creador
    
    Requiere: JWT válido en cabecera, creator_email en el cuerpo
    Retorna: confirmación o error
    """
    try:
        data: Dict[str, Any] = request.get_json()
        
        # Aceptar tanto creator_email como creator_username
        creator_email: Optional[str] = data.get("creator_email")
        creator_username: Optional[str] = data.get("creator_username")
        
        # Si viene username, convertir a email
        if creator_username and not creator_email:
            creator_data = mongo.db.users.find_one(
                {"username": creator_username, "role": "creator"},
                {"email": 1}
            )
            if not creator_data:
                return jsonify({"error": "Creador no encontrado"}), 404
            creator_email = creator_data["email"]
        
        # Si no viene ninguno, error
        if not creator_email:
            return jsonify({"error": "Email o username del creador requerido"}), 400
            
        follower_email: str = get_jwt_identity()
        
        # Verificar que el creador exista
        creator_data = find_by_email(creator_email)
        if not creator_data or creator_data.get("role") != "creator":
            return jsonify({"error": "Creador no encontrado"}), 404
            
        # Verificar que no se esté siguiendo a sí mismo
        if creator_email == follower_email:
            return jsonify({"error": "No puedes seguirte a ti mismo"}), 400
            
        # Verificar si ya lo sigue
        existing = mongo.db.followings.find_one({
            "follower_email": follower_email,
            "creator_email": creator_email
        })
        
        if existing:
            return jsonify({"message": "Ya sigues a este creador"}), 200
            
        # Crear la relación de seguimiento
        following = Following(
            follower_email=follower_email,
            creator_email=creator_email  # ← Sigue usando email internamente
        )
        
        mongo.db.followings.insert_one(following.to_dict())
        
        return jsonify({"message": f"Ahora sigues a {creator_data['username']}"}), 201
    except Exception as e:
        current_app.logger.error(f"[follow_creator] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@user_bp.route("/unfollow", methods=["POST"])
@role_required("follower")
def unfollow_creator() -> Tuple[Any, int]:
    """
    Deja de seguir a un creador
    
    Requiere: JWT válido en cabecera, creator_email en el cuerpo
    Retorna: confirmación o error
    """
    try:
        data: Dict[str, Any] = request.get_json()
        
        # Aceptar tanto creator_email como creator_username
        creator_email: Optional[str] = data.get("creator_email")
        creator_username: Optional[str] = data.get("creator_username")
        
        # Si viene username, convertir a email
        if creator_username and not creator_email:
            creator_data = mongo.db.users.find_one(
                {"username": creator_username, "role": "creator"},
                {"email": 1}
            )
            if not creator_data:
                return jsonify({"error": "Creador no encontrado"}), 404
            creator_email = creator_data["email"]
        
        if not creator_email:
            return jsonify({"error": "Email o username del creador requerido"}), 400
            
        follower_email: str = get_jwt_identity()
        
        # Buscar la relación de seguimiento
        following_data = mongo.db.followings.find_one({
            "follower_email": follower_email,
            "creator_email": creator_email
        })
        
        if not following_data:
            return jsonify({"message": "No estabas siguiendo a este creador"}), 404
            
        # Eliminar la relación de seguimiento
        mongo.db.followings.delete_one({
            "follower_email": follower_email,
            "creator_email": creator_email
        })
        
        return jsonify({"message": "Has dejado de seguir a este creador"}), 200
    except Exception as e:
        current_app.logger.error(f"[unfollow_creator] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@user_bp.route("/creators-list", methods=["GET"])
@role_required("follower")
def explore_creators() -> Tuple[Any, int]:
    """
    Muestra la lista de creadores que el follower está siguiendo
    
    Requiere: JWT válido en cabecera
    Query params opcionales: page, limit, sort (popular, recent)
    Retorna: lista paginada de creadores seguidos
    """
    try:
        email: str = get_jwt_identity()
        
        # Paginación
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 10))
        skip: int = (page - 1) * limit
        
        # Ordenación: popular o más reciente
        sort_by: str = request.args.get("sort", "recent")
        
        # 1. Obtener los emails de los creadores que sigue el usuario
        following_data = list(mongo.db.followings.find(
            {"follower_email": email},
            {"_id": 0, "creator_email": 1, "created_at": 1}
        ))
        
        # Extraer la lista de emails de creadores
        creator_emails: List[str] = [item["creator_email"] for item in following_data]
        
        if not creator_emails:
            return jsonify({
                "creators": [],
                "message": "No sigues a ningún creador. ¡Explora nuevos creadores!",
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }), 200
        
        # 2. Contar total de creadores seguidos
        total_creators: int = len(creator_emails)
        
        # 3. Preparar la búsqueda con los emails recolectados
        query = {"email": {"$in": creator_emails}, "role": "creator"}
        
        # Determinar el ordenamiento
        if sort_by == "popular":
            # Ordenar por popularidad (número de seguidores)
            # Necesitamos añadir esta información después de obtener los datos
            sort_criteria = [("username", 1)]  # Por defecto ordenamos por nombre
        else:  # recent - ordenar por fecha de seguimiento
            # Aquí necesitamos procesar manualmente después de obtener los datos
            sort_criteria = [("username", 1)]  # Ordenamos temporalmente por nombre
            
        # Obtener datos de los creadores seguidos
        creators_cursor = mongo.db.users.find(
            query,
            {"_id": 0, "password": 0}
        ).sort(sort_criteria).skip(skip).limit(limit)
        
        creators: List[Dict[str, Any]] = []
        for creator in creators_cursor:
            # Para cada creador, obtener datos adicionales como número de seguidores
            followers_count = mongo.db.followings.count_documents({"creator_email": creator["email"]})
            creator["followers_count"] = followers_count
            
            # Añadir fecha de seguimiento 
            follow_info = next((item for item in following_data if item["creator_email"] == creator["email"]), None)
            if follow_info and "created_at" in follow_info:
                creator["followed_at"] = follow_info["created_at"]
            
            # El usuario siempre sigue a estos creadores
            creator["following"] = True
            
            creators.append(creator)
            
        # Ordenar por fecha de seguimiento si se solicitó "recent"
        if sort_by == "recent" and creators:
            creators.sort(key=lambda x: x.get("followed_at", datetime.min), reverse=True)
        
        return jsonify({
            "creators": creators,
            "page": page,
            "limit": limit,
            "total": total_creators,
            "pages": (total_creators + limit - 1) // limit,
            "message": f"Mostrando {len(creators)} de {total_creators} creadores que sigues"
        }), 200
    except Exception as e:
        current_app.logger.error(f"[explore_creators] Error: {e}")
        return jsonify({"error": "Error al obtener creadores seguidos"}), 500


# RUTAS PARA CREADORES

@user_bp.route("/creator/<username>", methods=["GET"])
def public_creator_profile(username: str) -> Tuple[Any, int]:
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
    
# RUTAS PARA CREADORES

@user_bp.route("/creator/dashboard", methods=["GET"])
@role_required("creator")
def creator_dashboard() -> Tuple[Any, int]:
    """
    Panel del creador: estadísticas de seguidores y posts
    
    Requiere: JWT válido en cabecera, rol creator
    Retorna: estadísticas del creador (seguidores, posts)
    """
    try:
        email: str = get_jwt_identity()

        # Estadísticas del creador
        followers_count: int = mongo.db.followings.count_documents({"creator_email": email})
        posts_count: int = mongo.db.posts.count_documents({"creator_email": email})

        return jsonify({
            "stats": {
                "followers_count": followers_count,
                "posts_count": posts_count
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"[creator_dashboard] Error: {e}")
        return jsonify({"error": "Error al obtener el panel del creador"}), 500
    

@user_bp.route("/creator/followers", methods=["GET"])
@role_required("creator")
def get_creator_followers() -> Tuple[Any, int]:
    """
    Obtiene la lista de seguidores del creador autenticado
    
    Requiere: JWT válido en cabecera, rol creator
    Retorna: lista de seguidores con información básica
    """
    try:
        creator_email: str = get_jwt_identity()
        
        # Paginación
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 20))
        skip: int = (page - 1) * limit
        
        # Obtener total de seguidores
        total_followers = mongo.db.followings.count_documents({"creator_email": creator_email})
        
        # Obtener emails de seguidores con paginación
        followers_cursor = mongo.db.followings.find(
            {"creator_email": creator_email},
            {"_id": 0, "follower_email": 1, "created_at": 1}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        followers_data = list(followers_cursor)
        
        # Obtener información de los usuarios seguidores
        followers_list = []
        for follow_record in followers_data:
            follower = mongo.db.users.find_one(
                {"email": follow_record["follower_email"]},
                {"_id": 0, "email": 0, "password": 0, "role": 0}  # Excluir información sensible
            )
            if follower:
                followers_list.append({
                    "username": follower.get("username", "Usuario"),
                    "avatar_url": follower.get("avatar_url", ""),
                    "followed_at": follow_record["created_at"]
                })
        
        return jsonify({
            "followers": followers_list,
            "page": page,
            "limit": limit,
            "total": total_followers,
            "pages": (total_followers + limit - 1) // limit
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[get_creator_followers] Error: {e}")
        return jsonify({"error": "Error al obtener los seguidores"}), 500


@user_bp.route("/creator/update-profile", methods=["PUT"])
@role_required("creator")
def update_creator_profile() -> Tuple[Any, int]:
    """Actualizar perfil del creador"""
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()
        allowed_fields: List[str] = ["bio", "avatar_url", "username"]  # CORREGIDO: eliminado email por complejidad

        update_data: Dict[str, Any] = {k: v for k, v in data.items() if k in allowed_fields}
        if not update_data:
            return jsonify({"error": "No se proporcionaron datos válidos para actualizar"}), 400
        
        # Verificar si el username ya existe (para otro usuario)
        if "username" in update_data:
            existing = mongo.db.users.find_one({"username": update_data["username"], "email": {"$ne": email}})
            if existing:
                return jsonify({"error": "El nombre de usuario ya está en uso"}), 409
            
        # Actualizar perfil
        result = mongo.db.users.update_one(
            {"email": email},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({"message": "Perfil de creador actualizado con éxito"}), 200
        else:
            return jsonify({"message": "No se realizaron cambios en el perfil"}), 200

    except Exception as e:
        current_app.logger.error(f"[update_creator_profile] Error: {e}")  # CORREGIDO: f-string
        return jsonify({"error": "Error al actualizar el perfil"}), 500

@user_bp.route("/creator/create-post", methods=["POST"])
@role_required("creator")
def create_post() -> Tuple[Any, int]:
    """
    Crear un nuevo post en el perfil del creador
    
    Requiere: JWT válido en cabecera (validado por role_required)
    Campos requeridos: title, content
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()

        required_fields: List[str] = ["title", "content"]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos requeridos (title, content)"}), 400

        # Crear post usando el modelo Post
        post = Post(
            creator_email=email,
            title=data["title"],
            content=data["content"],
            media_urls=data.get("media_urls", [])
        )

        # Convertir a diccionario para guardar
        post_dict = post.to_dict()
        
        # Guardar el post en la base de datos
        result = mongo.db.posts.insert_one(post_dict)
        
        return jsonify({
            "message": "Post creado con éxito",
            "post_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        current_app.logger.error(f"[create_post] Error: {e}")
        return jsonify({"error": "Error al crear el post"}), 500
    
@user_bp.route("/creator/posts/<username>", methods=["GET"])
def get_creator_posts(username: str) -> Tuple[Any, int]:
    """Obtener posts de un creador por su username"""
    try:
        # Paginación
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 10))
        skip: int = (page - 1) * limit

        # Obtener email del creador - CORREGIDO: estructura de find_one
        creator = mongo.db.users.find_one({"username": username, "role": "creator"})
        if not creator:
            return jsonify({"error": "Creador no encontrado"}), 404
        email = creator["email"]

        # Total posts
        total_posts = mongo.db.posts.count_documents({"creator_email": email})

        # Obtener posts del creador - CORREGIDO: creator_email en lugar de author_email
        posts_cursor = mongo.db.posts.find({"creator_email": email}).sort("created_at", -1).skip(skip).limit(limit)        # Convertir el cursor a lista y formatear ObjectId - CORREGIDO: manipulación correcta
        posts: List[Dict[str, Any]] = []
        for post in posts_cursor:
            post_dict = dict(post)
            post_dict = process_post_for_json(post_dict)
            posts.append(post_dict)
        
        # Agregar información de likes usando la función utilitaria
        posts = add_like_info_to_posts(posts)
        
        return jsonify({
            "posts": posts,
            "page": page,
            "limit": limit,
            "total": total_posts,
            "pages": (total_posts + limit - 1) // limit            
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"[get_creator_posts] Error: {e}")
        return jsonify({"error": "Error al obtener los posts del creador"}), 500

@user_bp.route("/creator/delete-post/<post_id>", methods=["DELETE"])
@role_required("creator")
def delete_post(post_id: str) -> Tuple[Any, int]:
    """Eliminar un post del creador"""
    try:
        email: str = get_jwt_identity()

        # Verificar formato de ObjectId válido
        try:
            post_object_id = ObjectId(post_id)
        except Exception:
            return jsonify({"error": "ID de post inválido"}), 400

        # Verificar que el post existe y pertenece al creador - CORREGIDO: estructura de query
        post = mongo.db.posts.find_one({
            "_id": post_object_id, 
            "creator_email": email
        })
        
        if not post:
            return jsonify({"error": "Post no encontrado o no autorizado"}), 404
        
        # Eliminar post
        mongo.db.posts.delete_one({"_id": post_object_id})
        return jsonify({"message": "Post eliminado correctamente"}), 200
    except Exception as e:
        current_app.logger.error(f"[delete_post] Error: {e}")
        return jsonify({"error": "Error al eliminar post"}), 500

@user_bp.route("/wallets", methods=["POST"])
@role_required("creator")
def add_creator_wallet() -> Tuple[Any, int]:
    """
    Añade una nueva dirección de wallet para el creador
    
    Requiere: JWT válido en cabecera, rol creator
              currency_type, wallet_address
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()
        
        # Validar datos
        required_fields = ["currency_type", "wallet_address"]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan datos requeridos"}), 400
        
        # Validar que la moneda sea soportada
        if data["currency_type"] not in CreatorWallet.SUPPORTED_CURRENCIES:
            return jsonify({
                "error": f"Tipo de moneda no soportada. Use: {CreatorWallet.SUPPORTED_CURRENCIES}"
            }), 400
            
        # Validar que la wallet no exista ya para este creador y tipo de moneda
        existing = mongo.db.creator_wallets.find_one({
            "creator_email": email,
            "currency_type": data["currency_type"]
        })
        
        if existing:
            return jsonify({
                "error": f"Ya tienes una wallet configurada para {data['currency_type']}"
            }), 409
            
        # Crear wallet usando el modelo
        wallet = CreatorWallet(
            creator_email=email,
            wallet_address=data["wallet_address"],
            currency_type=data["currency_type"]
        )
        
        # Guardar en la base de datos
        mongo.db.creator_wallets.insert_one(wallet.to_dict())
        
        return jsonify({
            "message": f"Wallet de {data['currency_type']} añadida con éxito"
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.error(f"[add_creator_wallet] Error: {e}")
        return jsonify({"error": "Error al añadir wallet"}), 500


@user_bp.route("/wallets", methods=["GET"])
@role_required("creator")
def get_creator_wallets() -> Tuple[Any, int]:
    """
    Obtiene todas las direcciones de wallet del creador autenticado
    
    Requiere: JWT válido en cabecera, rol creator
    Retorna: lista de wallets configuradas
    """
    try:
        email: str = get_jwt_identity()
        
        # Buscar wallets del creador
        wallets_cursor = mongo.db.creator_wallets.find({"creator_email": email})
        
        # Formatear respuesta
        wallets: List[Dict[str, Any]] = []
        for wallet in wallets_cursor:
            # Convertir ObjectId a string para JSON
            if "_id" in wallet:
                wallet["_id"] = str(wallet["_id"])
            wallets.append(wallet)
        
        if not wallets:
            return jsonify({
                "message": "No tienes wallets configuradas",
                "wallets": []
            }), 200
            
        return jsonify({
            "message": "Wallets recuperadas con éxito",
            "wallets": wallets
        }), 200
    except Exception as e:
        current_app.logger.error(f"[get_creator_wallets] Error: {e}")
        return jsonify({"error": "Error al obtener las wallets"}), 500


@user_bp.route("/wallets/<currency_type>", methods=["GET"])
@role_required("creator")
def get_creator_wallet(currency_type: str) -> Tuple[Any, int]:
    """
    Obtiene una wallet específica por tipo de moneda
    
    Requiere: JWT válido en cabecera, rol creator
              currency_type en la URL
    Retorna: datos de la wallet o error
    """
    try:
        email: str = get_jwt_identity()
        
        # Validar que la moneda sea soportada
        if currency_type not in CreatorWallet.SUPPORTED_CURRENCIES:
            return jsonify({
                "error": f"Tipo de moneda no soportada. Use: {CreatorWallet.SUPPORTED_CURRENCIES}"
            }), 400
        
        # Buscar la wallet específica
        wallet = mongo.db.creator_wallets.find_one({
            "creator_email": email,
            "currency_type": currency_type
        })
        
        if not wallet:
            return jsonify({
                "error": f"No tienes una wallet configurada para {currency_type}"
            }), 404
            
        # Convertir ObjectId a string para JSON
        if "_id" in wallet:
            wallet["_id"] = str(wallet["_id"])
            
        return jsonify({
            "message": f"Wallet de {currency_type} recuperada",
            "wallet": wallet
        }), 200
    except Exception as e:
        current_app.logger.error(f"[get_creator_wallet] Error: {e}")
        return jsonify({"error": "Error al obtener la wallet"}), 500


@user_bp.route("/wallets/<currency_type>", methods=["PUT"])
@role_required("creator")
def update_creator_wallet(currency_type: str) -> Tuple[Any, int]:
    """
    Actualiza una wallet existente del creador
    
    Requiere: JWT válido en cabecera, rol creator
              currency_type en la URL
              wallet_address en el cuerpo
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json()
        
        # Validar datos
        if not data or "wallet_address" not in data:
            return jsonify({"error": "Dirección de wallet requerida"}), 400
            
        # Validar que la moneda sea soportada
        if currency_type not in CreatorWallet.SUPPORTED_CURRENCIES:
            return jsonify({
                "error": f"Tipo de moneda no soportada. Use: {CreatorWallet.SUPPORTED_CURRENCIES}"
            }), 400
            
        # Verificar que la wallet existe
        existing = mongo.db.creator_wallets.find_one({
            "creator_email": email,
            "currency_type": currency_type
        })
        
        if not existing:
            return jsonify({
                "error": f"No tienes una wallet configurada para {currency_type}"
            }), 404
            
        # Actualizar dirección de wallet
        result = mongo.db.creator_wallets.update_one(
            {
                "creator_email": email,
                "currency_type": currency_type
            },
            {
                "$set": {
                    "wallet_address": data["wallet_address"],
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            return jsonify({
                "message": f"Wallet de {currency_type} actualizada con éxito"
            }), 200
        else:
            return jsonify({
                "message": "No se realizaron cambios en la wallet"
            }), 200
    except Exception as e:
        current_app.logger.error(f"[update_creator_wallet] Error: {e}")
        return jsonify({"error": "Error al actualizar la wallet"}), 500


@user_bp.route("/wallets/<currency_type>", methods=["DELETE"])
@role_required("creator")
def delete_creator_wallet(currency_type: str) -> Tuple[Any, int]:
    """
    Elimina una wallet del creador
    
    Requiere: JWT válido en cabecera, rol creator
              currency_type en la URL
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        
        # Validar que la moneda sea soportada
        if currency_type not in CreatorWallet.SUPPORTED_CURRENCIES:
            return jsonify({
                "error": f"Tipo de moneda no soportada. Use: {CreatorWallet.SUPPORTED_CURRENCIES}"
            }), 400
            
        # Verificar que la wallet existe
        existing = mongo.db.creator_wallets.find_one({
            "creator_email": email,
            "currency_type": currency_type
        })
        
        if not existing:
            return jsonify({
                "error": f"No tienes una wallet configurada para {currency_type}"
            }), 404
            
        # Eliminar wallet
        result = mongo.db.creator_wallets.delete_one({
            "creator_email": email,
            "currency_type": currency_type
        })
        
        if result.deleted_count > 0:
            return jsonify({
                "message": f"Wallet de {currency_type} eliminada con éxito"
            }), 200
        else:
            return jsonify({
                "error": "No se pudo eliminar la wallet"
            }), 500
    except Exception as e:
        current_app.logger.error(f"[delete_creator_wallet] Error: {e}")
        return jsonify({"error": "Error al eliminar la wallet"}), 500


@user_bp.route("/wallets/set-default/<currency_type>", methods=["PUT"])
@role_required("creator")
def set_default_wallet(currency_type: str) -> Tuple[Any, int]:
    """
    Establece una wallet como predeterminada para el creador
    
    Requiere: JWT válido en cabecera, rol creator
              currency_type en la URL
    Retorna: confirmación o error
    """
    try:
        email: str = get_jwt_identity()
        
        # Validar que la moneda sea soportada
        if currency_type not in CreatorWallet.SUPPORTED_CURRENCIES:
            return jsonify({
                "error": f"Tipo de moneda no soportada. Use: {CreatorWallet.SUPPORTED_CURRENCIES}"
            }), 400
            
        # Verificar que la wallet existe
        existing = mongo.db.creator_wallets.find_one({
            "creator_email": email,
            "currency_type": currency_type
        })
        
        if not existing:
            return jsonify({
                "error": f"No tienes una wallet configurada para {currency_type}"
            }), 404
            
        # Primero, desmarcar cualquier wallet predeterminada actual
        mongo.db.creator_wallets.update_many(
            {"creator_email": email},
            {"$set": {"is_default": False}}
        )
        
        # Marcar la wallet seleccionada como predeterminada
        result = mongo.db.creator_wallets.update_one(
            {
                "creator_email": email,
                "currency_type": currency_type
            },
            {"$set": {"is_default": True}}
        )
        
        if result.modified_count > 0:
            return jsonify({
                "message": f"Wallet de {currency_type} establecida como predeterminada"
            }), 200
        else:
            return jsonify({
                "error": "No se pudo establecer la wallet como predeterminada"
            }), 500
    except Exception as e:
        current_app.logger.error(f"[set_default_wallet] Error: {e}")
        return jsonify({"error": "Error al establecer la wallet predeterminada"}), 500


@user_bp.route("/creator/<username>/donation-info", methods=["GET"])
def get_creator_donation_info(username: str) -> Tuple[Any, int]:
    """
    Obtiene información pública sobre las wallets de un creador para donaciones
    
    Requiere: username del creador en la URL
    Retorna: información de donación, incluyendo wallets disponibles
    """
    try:        # Buscar creador por username
        creator = mongo.db.users.find_one(
            {"username": username, "role": "creator"},
            {"_id": 0, "password": 0}  # Solo excluir campos sensibles
        )
        
        if not creator:
            return jsonify({"error": "Creador no encontrado"}), 404
            
        # Buscar wallets del creador
        wallets_cursor = mongo.db.creator_wallets.find(
            {"creator_email": creator["email"]},
            {"_id": 0, "creator_email": 0}  # No exponer el email del creador
        )
        
        wallets = list(wallets_cursor)
        
        # Obtener wallet predeterminada si existe
        default_wallet = next((w for w in wallets if w.get("is_default")), None)
        if not default_wallet and wallets:
            default_wallet = wallets[0]  # Si no hay predeterminada, usar la primera
            
        # Crear lista de métodos de donación disponibles
        available_currencies = [w["currency_type"] for w in wallets]
        
        # Eliminar el email del creador de la respuesta por seguridad
        if "email" in creator:
            del creator["email"]
            
        return jsonify({
            "creator": creator,
            "wallets": wallets,
            "default_wallet": default_wallet,
            "available_currencies": available_currencies
        }), 200
    except Exception as e:
        current_app.logger.error(f"[get_creator_donation_info] Error: {e}")
        return jsonify({"error": "Error al obtener información de donación"}), 500


# RUTAS PARA SISTEMA DE LIKES

@user_bp.route("/like-post", methods=["POST"])
@jwt_required()
def toggle_like_post() -> Tuple[Any, int]:
    """
    Alterna el like de un post (dar/quitar like)
    
    Requiere: JWT válido en cabecera, post_id en el cuerpo
    Retorna: estado del like y nuevo conteo
    """
    try:
        data: Dict[str, Any] = request.get_json()
        post_id: Optional[str] = data.get("post_id")
        
        if not post_id:
            return jsonify({"error": "post_id es requerido"}), 400
        
        user_email: str = get_jwt_identity()
        
        # Verificar si el post existe
        from bson import ObjectId
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"error": "post_id inválido"}), 400
            
        post_exists = mongo.db.posts.find_one({"_id": post_object_id})
        if not post_exists:
            return jsonify({"error": "Post no encontrado"}), 404
        
        # Verificar si ya existe el like
        existing_like = mongo.db.likes.find_one({
            "user_email": user_email,
            "post_id": post_id
        })
        
        if existing_like:
            # Quitar like
            mongo.db.likes.delete_one({
                "user_email": user_email,
                "post_id": post_id
            })
            liked = False
            action = "removed"
        else:
            # Agregar like
            like = Like(user_email, post_id)
            mongo.db.likes.insert_one(like.to_dict())
            liked = True
            action = "added"
        
        # Contar total de likes para este post
        total_likes = mongo.db.likes.count_documents({"post_id": post_id})
        
        return jsonify({
            "liked": liked,
            "likes_count": total_likes,
            "action": action,
            "message": f"Like {action} successfully"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[toggle_like_post] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@user_bp.route("/post/<post_id>/likes", methods=["GET"])
def get_post_likes(post_id: str) -> Tuple[Any, int]:
    """
    Obtiene información de likes de un post específico
    
    Requiere: post_id en la URL
    Retorna: conteo total y si el usuario actual le dio like (si está autenticado)
    """
    try:
        # Verificar si el post existe
        from bson import ObjectId
        try:
            post_object_id = ObjectId(post_id)
        except:
            return jsonify({"error": "post_id inválido"}), 400
            
        post_exists = mongo.db.posts.find_one({"_id": post_object_id})
        if not post_exists:
            return jsonify({"error": "Post no encontrado"}), 404
        
        # Contar total de likes
        total_likes = mongo.db.likes.count_documents({"post_id": post_id})
        
        # Verificar si el usuario actual le dio like (si está autenticado)
        user_liked = False
        try:
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_email = get_jwt_identity()
            if user_email:
                user_like = mongo.db.likes.find_one({
                    "user_email": user_email,
                    "post_id": post_id
                })
                user_liked = user_like is not None
        except:
            # Usuario no autenticado o token inválido
            pass
        
        return jsonify({
            "post_id": post_id,
            "likes_count": total_likes,
            "user_liked": user_liked
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[get_post_likes] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

