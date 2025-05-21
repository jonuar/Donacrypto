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
from ..extensions import mongo

user_bp = Blueprint("user_bp", __name__)

# FUNCIONES AUXILIARES

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
                "page": page,
                "pages": 0,
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
            # Convertir ObjectId a string para serialización JSON
            post["_id"] = str(post["_id"])
            
            # Obtener información básica del creador
            creator = mongo.db.users.find_one(
                {"email": post["creator_email"]},
                {"_id": 0, "username": 1, "avatar_url": 1}
            )
            
            if creator:
                post["creator_username"] = creator["username"]
                post["creator_avatar"] = creator.get("avatar_url", "")
                
            posts.append(post)
            
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
    """Sigue a un creador
    Requiere: JWT válido en cabecera, creator_email en el cuerpo
    """
    try:
        data: Dict[str, Any] = request.get_json()
        creator_email: Optional[str] = data.get("creator_email")
        
        if not creator_email:
            return jsonify({"error": "Email del creador requerido"}), 400
            
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
            
        # Crea la relación de seguimiento usando el modelo
        follow_data: Dict[str, Any] = {
            "follower_email": follower_email,
            "creator_email": creator_email,
            "created_at": datetime.now()
        }
        
        mongo.db.followings.insert_one(follow_data)
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
        creator_email: Optional[str] = data.get("creator_email")
        
        if not creator_email:
            return jsonify({"error": "Email del creador requerido"}), 400
            
        follower_email: str = get_jwt_identity()
        
        # Elimina la relación de seguimiento
        result = mongo.db.followings.delete_one({
            "follower_email": follower_email,
            "creator_email": creator_email
        })
        
        if result.deleted_count > 0:
            return jsonify({"message": "Has dejado de seguir a este creador"}), 200
        else:
            return jsonify({"message": "No estabas siguiendo a este creador"}), 404
    except Exception as e:
        current_app.logger.error(f"[unfollow_creator] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@user_bp.route("/explorers/creators", methods=["GET"])
@role_required("follower")
def explore_creators() -> Tuple[Any, int]:
    """
    Muestra una lista de creadores para explorar
    
    Requiere: JWT válido en cabecera
    Query params opcionales: page, limit, sort (popular, newest)
    Retorna: lista paginada de creadores
    """
    try:
        email: str = get_jwt_identity()
        
        # Paginación
        page: int = int(request.args.get("page", 1))
        limit: int = int(request.args.get("limit", 10))
        skip: int = (page - 1) * limit
        
        # Ordenación: popular o más nuevo
        sort_by: str = request.args.get("sort", "popular")
        
        # Query principal: todos los creadores
        query = {"role": "creator"}
        
        # Contar total de creadores
        total_creators = mongo.db.users.count_documents(query)
        
        # Determinar el ordenamiento
        sort_criteria = []
        if sort_by == "popular":
            # Para ordenar por popularidad, podríamos considerar el número de seguidores
            # Esto requeriría una operación de agregación más compleja
            # Por simplificar, ordenaremos por username alfabéticamente
            sort_criteria = [("username", 1)]
        else:  # newest
            sort_criteria = [("created_at", -1)]
            
        # Obtener datos
        creators_cursor = mongo.db.users.find(
            query,
            {"_id": 0, "password": 0}
        ).sort(sort_criteria).skip(skip).limit(limit)
        
        creators: List[Dict[str, Any]] = []
        for creator in creators_cursor:
            # Para cada creador, podemos obtener datos adicionales como número de seguidores
            followers_count = mongo.db.followings.count_documents({"creator_email": creator["email"]})
            creator["followers_count"] = followers_count
            
            # Verificar si el usuario actual sigue a este creador
            creator["following"] = mongo.db.followings.find_one({
                "follower_email": email,
                "creator_email": creator["email"]
            }) is not None
            
            creators.append(creator)
            
        return jsonify({
            "creators": creators,
            "page": page,
            "limit": limit,
            "total": total_creators,
            "pages": (total_creators + limit - 1) // limit
        }), 200
    except Exception as e:
        current_app.logger.error(f"[explore_creators] Error: {e}")
        return jsonify({"error": "Error al explorar creadores"}), 500


# RUTAS PARA CREATORS

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
    
# ARREGLAR DATOS DE DASHBOARD
@user_bp.route("/creator/dashboard", methods=["GET"])
@role_required("creator")
def creator_dashboard() -> Tuple[Any, int]:
    """Panel del creador: ver estadísticas"""
    try:
        email = get_jwt_identity()

        # Calcular estadísticas:
        # - Número de seguidores
        # - Likes en posts, etc.

        return jsonify({
            # "stats": {
            #     "total_donations": total_donations,
            #     "total_received": total_amount,
            #     "followers_count": followers_count,
            #     "posts_count": posts_count
            # }
        }), 200

    except Exception as e:
        current_app.logger.error(f"[creator_dashboard] Error: {e}")
        return jsonify({"error": "Error al obtener el panel del creador"}), 500
    

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
        posts_cursor = mongo.db.posts.find({"creator_email": email}).sort("created_at", -1).skip(skip).limit(limit)
        
        # Convertir el cursor a lista y formatear ObjectId - CORREGIDO: manipulación correcta
        posts: List[Dict[str, Any]] = []
        for post in posts_cursor:
            post_dict = dict(post)
            post_dict["_id"] = str(post_dict["_id"])
            posts.append(post_dict)
        
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

