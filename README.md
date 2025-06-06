# 🚀 DonaCrypto - Plataforma de Donaciones para Creadores de Contenido

Una alternativa descentralizada donde los creadores pueden recibir donaciones directamente en sus wallets de criptomonedas, con funcionalidades completas de red social.

---

## ⚙️ Tecnologías Usadas

### Backend
- **Framework:** Flask + Flask-RESTful
- **Base de datos:** MongoDB + PyMongo
- **Autenticación:** JWT (Flask-JWT-Extended)
- **Seguridad:** bcrypt, Flask-CORS
- **Validación:** python-dotenv

### Frontend
- **Framework:** Vue.js 3 + Composition API
- **Estado:** Pinia
- **Router:** Vue Router 4
- **HTTP Client:** Axios
- **UI:** Headless UI + Heroicons
- **Estilos:** SASS
- **Utilidades:** date-fns, qrcode, vue-toastification

---

## ✅ Funcionalidades Implementadas

### 🔐 Autenticación y Seguridad
- Registro de usuario (`POST /auth/register`)
- Inicio de sesión con JWT (`POST /auth/login`)
- Cierre de sesión con invalidación de token (`POST /auth/logout`)
- Protección de rutas privadas con `@jwt_required`
- Middleware de roles (`role_required`)
- Store de autenticación con Pinia (frontend)
- Cambio de contraseña para usuarios autenticados (`PUT /user/change-password`)
- **Eliminación completa de cuenta** con confirmación de contraseña (`DELETE /user/delete-account`)

### 👤 Gestión de Usuarios y Perfiles
- Obtener perfil actual (`GET /user/profile`)
- Actualizar perfil de follower (`PUT /user/update-profile`)
- Actualizar perfil de creador (`PUT /user/creator/update-profile`)
- Subida de avatar con preview
- Edición de username, bio y contraseña
- Validación de formularios
- **Zona de peligro** con eliminación de cuenta y confirmación de contraseña

### 🎨 Sistema de Posts Completo
- Crear publicaciones (`POST /user/posts`)
- Obtener publicaciones (`GET /user/posts/<username>`)
- Eliminar publicaciones (`DELETE /user/posts/<post_id>`)
- Component PostCard reutilizable
- Paginación en feeds y dashboards
- Funcionalidad de likes (simulada)
- Compartir posts

### 💰 Gestión de Wallets
- Agregar/editar/eliminar wallets (`POST/PUT/DELETE /user/wallets`)
- Generación de códigos QR
- Soporte para múltiples criptomonedas (BTC, ETH, USDT)
- Vista de wallets en perfil público

### 👥 Sistema de Seguimiento
- Seguir creador (`POST /user/follow`)
- Dejar de seguir (`POST /user/unfollow`)
- Lista de creadores seguidos (`GET /user/following`)
- Lista paginada con estadísticas (`GET /user/creators-list`)

### 🔍 Búsqueda y Exploración
- Buscar creadores por username (`GET /user/search-creators`)
- Explorar todos los creadores (`GET /user/explore-all-creators`)
- Ordenación por popularidad, reciente, alfabético
- Paginación en resultados de búsqueda

### 📰 Feed Personalizado
- Feed con posts de creadores seguidos (`GET /user/feed`)
- Paginación de posts
- Enlaces a perfiles de creadores
- Estado vacío cuando no sigue a nadie

### 🎯 Frontend Completo
- **Dashboard de Creador:** Gestión completa de posts y wallets
- **Feed de Seguidor:** Posts personalizados de creadores seguidos
- **Explorar Creadores:** Búsqueda y seguimiento en tiempo real
- **Perfil de Seguidor:** Gestión completa de perfil y configuración
- **Perfil Público:** Vista pública de creadores con posts y wallets
- **Navegación dinámica:** Basada en roles de usuario
- **Diseño responsivo:** Optimizado para móviles y desktop

---

## 📁 Estructura del Proyecto

### Backend
```
backend/
├── app.py
├── requirements.txt
├── wsgi.py
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── decorators/
│   │   └── role_required.py
│   ├── models/
│   │   ├── user.py
│   │   ├── creator_wallet.py
│   │   ├── post.py
│   │   ├── like.py
│   │   └── following.py
│   ├── utils/
│   │   └── like_utils.py
│   └── routes/
│       ├── auth_routes.py
│       └── user_routes.py
```

### Frontend
```
frontend/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── auth.js
│   │   ├── counter.js
│   │   └── dashboard.js
│   ├── views/
│   │   ├── HomeView.vue
│   │   ├── AboutView.vue
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   ├── creator/
│   │   │   ├── CreatorDashboard.vue
│   │   │   └── CreatorPublicProfile.vue
│   │   └── follower/
│   │       ├── FollowerFeed.vue
│   │       ├── ExploreCreators.vue
│   │       └── FollowerProfile.vue
│   ├── components/
│   │   ├── auth/
│   │   │   └── AuthComponent.vue
│   │   └── common/
│   │       ├── PostCard.vue
│   │       └── DeleteAccountModal.vue
│   ├── services/
│   │   └── api.js
│   └── assets/
│       └── styles/
│           └── style.scss
├── package.json
└── vite.config.js
```

---

## 🚀 Instalación y Configuración

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📋 API Endpoints

### Auth
```http
POST /auth/register    # Registro de usuario
POST /auth/login       # Inicio de sesión
POST /auth/logout      # Cierre de sesión
```

### Usuarios
```http
GET /user/profile                  # Obtener perfil actual
PUT /user/update-profile           # Actualizar perfil de follower
PUT /user/creator/update-profile   # Actualizar perfil de creador
PUT /user/change-password          # Cambiar contraseña
DELETE /user/delete-account        # Eliminar cuenta
POST /user/posts                   # Crear publicación
GET /user/posts/<username>         # Obtener posts de usuario
DELETE /user/posts/<post_id>       # Eliminar post
POST /user/wallets                 # Agregar wallet
PUT /user/wallets/<wallet_id>      # Editar wallet
DELETE /user/wallets/<wallet_id>   # Eliminar wallet
GET /user/wallets/<username>       # Ver wallets públicas
POST /user/follow                  # Seguir creador
POST /user/unfollow               # Dejar de seguir
GET /user/following               # Lista de seguidos
GET /user/creators-list           # Lista de creadores con stats
GET /user/search-creators         # Buscar creadores
GET /user/explore-all-creators    # Explorar todos los creadores
GET /user/feed                    # Feed personalizado
```

---

## 🔒 Características de Seguridad

### 
- **Autenticación JWT** con tokens de larga duración opcionales (30 días con "Recordarme")
- **Validación de contraseñas** con longitud mínima y cifrado bcrypt
- **Protección de rutas** basada en roles (creator/follower)
- **Blacklist de tokens** para logout seguro
- **Confirmación de contraseña** para operaciones críticas (eliminación de cuenta)
- **Validación de entrada** en todos los endpoints
- **Gestión segura de sesiones** con almacenamiento local/sesión


> **Nota**: Los usuarios solo pueden cambiar su contraseña si están autenticados y conocen la actual.

---

## 🏗️ Próximos Pasos
- Sistema de donaciones real con blockchain
- Integración con wallets (Metamask)
- Sistema de notificaciones
- Comentarios en posts
- Sistema de likes real
- Panel de analíticas para creadores
- Sistema de búsqueda avanzada
- Modo oscuro
- PWA (Progressive Web App)

---

## 📈 Estado Actual del Proyecto

### ✅ Completado
- ✅ Sistema de autenticación completo (registro, login, logout)
- ✅ Gestión de perfiles para creadores y followers
- ✅ Sistema de posts con CRUD completo
- ✅ Gestión de wallets de criptomonedas
- ✅ Sistema de seguimiento entre usuarios
- ✅ Feed personalizado y exploración de creadores
- ✅ **Eliminación completa de cuenta** con confirmación
- ✅ **Cambio de contraseña** para usuarios autenticados
- ✅ Interfaz responsive y moderna
- ✅ **Remoción de funcionalidad de recuperación de contraseña**

### 🔧 Configuración de Desarrollo
```bash
# Backend (Puerto 5000)
cd backend
python app.py

# Frontend (Puerto 5173) 
cd frontend
npm run dev
```

### 🎯 Funcionalidades Principales Verificadas
- [x] Registro y login de usuarios
- [x] Dashboard completo para creadores
- [x] Feed personalizado para followers
- [x] Exploración y seguimiento de creadores
- [x] Gestión de posts y wallets
- [x] Perfiles públicos y privados
- [x] Eliminación segura de cuentas
- [x] Cambio de contraseñas

---

## 📜 Licencia
MIT



