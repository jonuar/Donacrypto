from flask import Flask, jsonify, request
from flask_cors import CORS
from .extensions import mongo, jwt
import logging
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from bson import ObjectId

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logging basada en entorno
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO)
if os.getenv('FLASK_ENV') == 'production':
    log_level = logging.DEBUG

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Configurar encoder JSON personalizado para manejar datetime y ObjectId
    from flask.json.provider import DefaultJSONProvider
    
    class CustomJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, ObjectId):
                return str(obj)
            return super().default(obj)
    
    app.json = CustomJSONProvider(app)    # Config seguridad - Usa variables de entorno
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    if not app.config["SECRET_KEY"]:
        if os.getenv('FLASK_ENV') == 'production':
            raise ValueError("SECRET_KEY debe estar configurada como variable de entorno en producción")
        else:
            app.config["SECRET_KEY"] = "clave-secreta-development"
            logger.warning("Usando SECRET_KEY por defecto - NO usar en producción")
    
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]
    
    # Configurar tiempo de expiración del token JWT
    jwt_expires = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))  # 24 horas por defecto
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=jwt_expires)

    # MongoDB config - Usar MONGO_URI de variables de entorno
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        if os.getenv('FLASK_ENV') == 'production':
            raise ValueError("MONGO_URI debe estar configurada como variable de entorno en producción")
        else:
            mongo_uri = "mongodb://localhost:27017/db_plataforma_donaciones"
            logger.warning("Usando MongoDB local por defecto - NO usar en producción")
    
    # app.config["MONGO_URI"] = mongo_uri    # Inicializa extensiones
    # mongo.init_app(app)
    # jwt.init_app(app)

    app.config["MONGO_URI"] = mongo_uri
    app.config["MONGODB_DB"] = os.getenv("MONGO_DB_NAME", "db_plataforma_donaciones")
    
    # Inicialización de extensiones
    try:
        # Inicializa primero MongoDB
        mongo.init_app(app)
        
        # Luego inicializa JWT
        jwt.init_app(app)
        
        # Verifica la conexión dentro del contexto de la aplicación
        with app.app_context():
            # Usa el cliente directamente para hacer ping
            client = mongo.cx
            client.admin.command('ping')
            logger.info(f"MongoDB conectado exitosamente a: {app.config['MONGODB_DB']}")
    except Exception as e:
        logger.error(f"Error de conexión MongoDB: {str(e)}")
        if os.getenv('FLASK_ENV') == 'production':
            raise
        else:
            logger.warning("Continuando sin MongoDB en modo desarrollo")
    
    # CORS configurado para producción y desarrollo
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    if os.getenv('FLASK_ENV') == 'production':
        CORS(app, resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False
        }
    })
        logger.info(f"CORS configurado para producción con orígenes: {allowed_origins}")
    else:
        CORS(app)
        logger.info("CORS configurado para desarrollo (todos los orígenes)")

    # Error handlers
    @app.errorhandler(500)
    def handle_500_error(e):
        logger.error(f"Error 500: {str(e)}")  # Log the error
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500

    @app.errorhandler(404)
    def handle_404_error(e):
        logger.warning(f"Error 404: {request.path}")  # Log the missing path
        return jsonify({
            "error": "Recurso no encontrado",
            "path": request.path
        }), 404

    # Importa y registra Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.health_routes import health_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(health_bp) # Ruta de salud para verificar el estado de la aplicación

    # Log de configuración exitosa
    logger.info(f"Aplicación Flask iniciada en modo: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"Base de datos: {app.config['MONGO_URI'].split('@')[1] if '@' in app.config['MONGO_URI'] else 'local'}")

    return app