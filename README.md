# 🚀 Plataforma de Donaciones para Creadores de Contenido

Una alternativa descentralizada donde los creadores pueden recibir donaciones directamente en sus wallets de criptomonedas.

---

## ⚙️ Tecnologías Usadas

- **Backend:** Flask + PyMongo
- **Frontend:** Vue.js + SASS
- **Base de datos:** MongoDB
- **Autenticación:** JWT (Json Web Tokens)
- **Criptografía:** bcrypt
- **Logs:** Python Logging

---

## ✅ Funcionalidades Implementadas

### 🔐 Autenticación y Seguridad
- Registro de usuario (`POST /auth/register`)
- Inicio de sesión con JWT (`POST /auth/login`)
- Protección de rutas privadas con `@jwt_required`
- Middleware de roles (`role_required`)

### 👤 Gestión de Usuarios y Creadores
- Obtener perfil actual (`GET /auth/me`)
- Gestión de wallets del creador (`POST /creator/wallets`)
- Lista de creadores seguidos (`GET /following/list`)
- Seguir creador (`POST /following/add`)

### 🧑‍🎨 Panel de Creador (Pendiente)
- Vista general de métricas
- Crear publicaciones (`POST /creator/posts`)
- Eliminar publicaciones (`DELETE /creator/posts/<post_id>`)
- Ver publicaciones públicas (`GET /creators/posts/<username>`)

---

## 📁 Estructura del Proyecto (backend)
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

## 🧪 Pruebas con Thunder Client / Postman (Pendiente)

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

---

## 🏗️ Próximos Pasos
- Integración con wallet (Metamask)
- Sistema de comentarios en posts
- Frontend Vue + diseño responsive
- Feed personalizado por seguidos
- Notificaciones por correo

---

## 📜 Licencia
MIT

