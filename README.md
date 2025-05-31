# 🚀 Plataforma de Donaciones para Creadores de Contenido

Una alternativa descentralizada donde los creadores pueden recibir donaciones directamente en sus wallets de criptomonedas.

---

## ⚙️ Tecnologías Usadas

- **Backend:** Flask + PyMongo
- **Frontend:** Vue.js 3 + Composition API + Pinia
- **Base de datos:** MongoDB
- **Autenticación:** JWT (Json Web Tokens)
- **Criptografía:** bcrypt
- **Logs:** Python Logging
- **Router:** Vue Router 4
- **HTTP Client:** Axios

---

## ✅ Funcionalidades Implementadas

### 🔐 Autenticación y Seguridad
- Registro de usuario (`POST /auth/register`)
- Inicio de sesión con JWT (`POST /auth/login`)
- Protección de rutas privadas con `@jwt_required`
- Middleware de roles (`role_required`)
- Store de autenticación con Pinia (frontend)

### 👤 Gestión de Usuarios y Creadores
- Obtener perfil actual (`GET /auth/me`)
- Gestión de wallets del creador (`POST /creator/wallets`)
- Lista de creadores seguidos (`GET /following/list`)
- Seguir creador (`POST /following/add`)

### 🎨 Frontend
- Aplicación Vue.js 3 configurada
- Sistema de rutas con Vue Router
- Store global de autenticación
- Diseño responsivo con SASS
- Inicialización automática de autenticación

### 🧑‍🎨 Panel de Creador (Pendiente)
- Vista general de métricas
- Crear publicaciones (`POST /creator/posts`)
- Eliminar publicaciones (`DELETE /creator/posts/<post_id>`)
- Ver publicaciones públicas (`GET /creators/posts/<username>`)

---

## 📁 Estructura del Proyecto

### Backend
```
backend/
├── app.py
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   │   ├── user.py
│   │   ├── creator_wallet.py
│   │   ├── post.py
│   │   └── following.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── creator_routes.py
│   │   └── following_routes.py
│   └── utils/
│       └── role_required.py
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
│   │   └── auth.js
│   ├── views/
│   ├── components/
│   └── assets/
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

### Auth
```http
POST /auth/register
POST /auth/login
GET /auth/me
```

### Creador
```http
POST /creator/wallets
GET /creator/dashboard
POST /creator/posts
DELETE /creator/posts/<post_id>
GET /creators/posts/<username>
```

### Following
```http
GET /following/list
POST /following/add
DELETE /following/remove
```



