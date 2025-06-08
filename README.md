# DonaCrypto

Una plataforma descentralizada de donaciones para creadores de contenido que permite recibir donaciones en criptomonedas directamente en sus wallets, con funcionalidades completas de red social.

## ✨ Características

- 🔐 **Autenticación segura** con JWT y bcrypt
- 👤 **Perfiles duales** para creadores y seguidores  
- 📝 **Sistema de publicaciones** con feed personalizado
- 💰 **Gestión de wallets** (BTC, ETH, USDT) con códigos QR
- 👥 **Red social** - seguir/dejar de seguir creadores
- 🔍 **Exploración y búsqueda** de creadores
- 📱 **Interfaz responsiva** optimizada para móviles
- 🛡️ **Seguridad avanzada** con eliminación de cuenta y cambio de contraseña

## 🛠️ Stack Tecnológico

### Backend
- **Framework:** Flask + Flask-RESTful
- **Base de datos:** MongoDB con PyMongo
- **Autenticación:** JWT (Flask-JWT-Extended)
- **Seguridad:** bcrypt, Flask-CORS
- **Utilidades:** python-dotenv

### Frontend
- **Framework:** Vue.js 3 con Composition API
- **Estado:** Pinia
- **Routing:** Vue Router 4
- **HTTP:** Axios
- **Estilos:** SASS
- **Utilidades:** date-fns, qrcode, vue-toastification

## 🚀 Instalación

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- MongoDB

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
El servidor estará disponible en `http://localhost:5000`

### Frontend  
```bash
cd frontend
npm install
npm run dev
```
La aplicación estará disponible en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
donacrypto/
├── backend/                    # API Flask
│   ├── app.py                 # Punto de entrada
│   ├── requirements.txt       # Dependencias Python
│   └── app/
│       ├── models/            # Modelos de datos
│       ├── routes/            # Endpoints de la API
│       ├── decorators/        # Middleware personalizado
│       └── utils/             # Utilidades
├── frontend/                   # Aplicación Vue.js
│   ├── src/
│   │   ├── components/        # Componentes reutilizables
│   │   ├── views/             # Páginas de la aplicación
│   │   ├── stores/            # Estado global (Pinia)
│   │   ├── router/            # Configuración de rutas
│   │   └── services/          # Servicios API
│   └── package.json
└── README.md
```

## 📡 API Endpoints

### Autenticación
```http
POST /auth/register    # Registro de usuario
POST /auth/login       # Inicio de sesión  
POST /auth/logout      # Cierre de sesión
```

### Usuarios y Perfiles
```http
GET  /user/profile              # Obtener perfil actual
PUT  /user/update-profile       # Actualizar perfil
PUT  /user/change-password      # Cambiar contraseña
DELETE /user/delete-account     # Eliminar cuenta
```

### Publicaciones
```http
POST /user/posts               # Crear publicación
GET  /user/posts/<username>    # Obtener posts de usuario
DELETE /user/posts/<post_id>   # Eliminar post
GET  /user/feed               # Feed personalizado
```

### Wallets
```http
POST /user/wallets             # Agregar wallet
PUT  /user/wallets/<id>        # Editar wallet  
DELETE /user/wallets/<id>      # Eliminar wallet
GET  /user/wallets/<username>  # Ver wallets públicas
```

### Red Social
```http
POST /user/follow              # Seguir creador
POST /user/unfollow            # Dejar de seguir
GET  /user/following           # Lista de seguidos
GET  /user/search-creators     # Buscar creadores
```

## 🔒 Características de Seguridad

- ✅ Autenticación JWT con tokens seguros
- ✅ Hash de contraseñas con bcrypt
- ✅ Protección de rutas basada en roles
- ✅ Blacklist de tokens para logout seguro
- ✅ Validación de entradas en todos los endpoints
- ✅ Confirmación de contraseña para operaciones críticas

## 🎯 Roadmap

- [ ] Integración con Metamask
- [ ] Sistema de notificaciones en tiempo real
- [ ] Comentarios en publicaciones
- [ ] Panel de analíticas para creadores
- [ ] Búsqueda avanzada con filtros
- [ ] Modo oscuro
- [ ] Progressive Web App (PWA)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.



