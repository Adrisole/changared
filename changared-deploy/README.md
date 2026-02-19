# 🚀 ChangaRed - Plataforma de Servicios Profesionales con IA

Plataforma inteligente que conecta clientes con profesionales (electricistas, plomeros, gasistas) usando IA para asignación automática y Mercado Pago para pagos.

## ✨ Características

- 🤖 **IA Integrada**: OpenAI GPT-4o-mini detecta tipo de servicio y asigna profesionales automáticamente
- 📍 **Geolocalización**: Asigna el profesional más cercano usando cálculo de distancia
- 💰 **Mercado Pago**: Pagos con comisión automática del 20%
- 🔐 **Autenticación Segura**: JWT con roles (cliente, profesional, admin)
- 📊 **Dashboard Admin**: Métricas en tiempo real, gestión de profesionales
- 🎨 **UI Moderna**: React con Shadcn UI y diseño profesional

## 🏗️ Stack Tecnológico

### Frontend
- React 19
- Tailwind CSS
- Shadcn UI
- React Router
- Axios

### Backend
- Python 3.11
- FastAPI
- MongoDB (Motor)
- Mercado Pago SDK
- OpenAI (vía Emergent Integrations)

## 📁 Estructura del Proyecto

```
changared/
├── backend/                 # FastAPI Backend
│   ├── server.py           # Servidor principal
│   ├── mercadopago_routes.py  # Rutas de pagos
│   ├── requirements.txt    # Dependencias Python
│   └── .env               # Variables de entorno
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # Componentes reutilizables
│   │   ├── pages/        # Páginas principales
│   │   └── contexts/     # Context API (Auth)
│   ├── package.json      # Dependencias Node
│   └── .env             # Variables de entorno
│
├── DEPLOYMENT.md         # Guía de deployment
└── README.md            # Este archivo
```

## 🚀 Instalación Local

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crear .env con tus credenciales
cp .env.example .env
nano .env

# Ejecutar
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install

# Crear .env
cp .env.example .env
nano .env

# Ejecutar
npm start
```

### 3. MongoDB

Opción A: **MongoDB Local**
```bash
# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongodb
```

Opción B: **MongoDB Atlas** (Recomendado)
1. Crea cuenta gratis en https://mongodb.com/atlas
2. Crea cluster gratuito
3. Obtén connection string
4. Agrégalo a backend/.env

## 🌐 Deployment en Producción

### Opción 1: Vercel + Railway (GRATIS) ⭐ Recomendado

#### Frontend en Vercel
```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

#### Backend en Railway
1. Ve a https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Selecciona carpeta: `backend`
4. Agrega variables de entorno
5. ¡Listo!

### Opción 2: VPS Propio

Ver guía completa en `DEPLOYMENT.md`

## 🔐 Variables de Entorno

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=changared
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-xxxxx
JWT_SECRET=tu-clave-secreta-cambiar
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=43200
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxxxx
MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxx
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxx
```

## 💳 Configuración de Mercado Pago

### Obtener Credenciales

1. Ve a https://www.mercadopago.com.ar/developers/panel
2. Crea una aplicación
3. Obtén:
   - **Access Token** (backend)
   - **Public Key** (frontend)

### Flujo de Comisión

1. Cliente paga $5000 → Tu cuenta MP recibe $5000
2. Sistema calcula: 20% comisión ($1000) + 80% profesional ($4000)
3. Tú transfieres $4000 al profesional (manual o automático)
4. Te quedas con $1000

## 📖 Uso de la Plataforma

### Para Clientes
1. Registrarse como "Cliente"
2. Crear solicitud describiendo el problema
3. IA asigna profesional automáticamente
4. Ver precio y pagar con Mercado Pago
5. Profesional recibe la asignación

### Para Profesionales
1. Registrarse como "Profesional"
2. Admin aprueba y configura ubicación
3. Recibir solicitudes automáticas
4. Completar servicios
5. Recibir pagos (80% del total)

### Para Admin
1. Dashboard con métricas en tiempo real
2. Gestión de profesionales (CRUD)
3. Ver todas las solicitudes
4. Control de comisiones ganadas

## 🧪 Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 📊 Funcionalidades Clave

### ✅ Gestión de Solicitudes
- Creación con descripción en lenguaje natural
- IA detecta tipo de servicio automáticamente
- Asignación por proximidad geográfica
- Cálculo automático de precios con urgencia

### ✅ Sistema de Pagos
- Integración completa con Mercado Pago
- Comisión automática del 20%
- Múltiples métodos de pago
- Webhooks para actualización en tiempo real

### ✅ Roles y Permisos
- **Cliente**: Solicitar servicios, ver historial
- **Profesional**: Ver asignaciones, estadísticas
- **Admin**: Control total, métricas, gestión

### ✅ Dashboard Administrativo
- Total de solicitudes
- Comisiones generadas
- Profesionales activos
- Gestión completa de profesionales

## 🛠️ Tecnologías y Librerías

### Backend
- FastAPI - Framework web
- Motor - MongoDB async driver
- Pydantic - Validación de datos
- PyJWT - Autenticación JWT
- Passlib - Hash de contraseñas
- Emergent Integrations - OpenAI wrapper
- Mercado Pago SDK - Pagos

### Frontend
- React - UI Library
- React Router - Navegación
- Tailwind CSS - Estilos
- Shadcn UI - Componentes
- Axios - HTTP client
- React Hook Form - Formularios
- Sonner - Notificaciones

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Verificar MongoDB
sudo systemctl status mongodb

# Ver logs
tail -f /var/log/supervisor/backend.err.log
```

### Frontend no conecta al backend
- Verificar REACT_APP_BACKEND_URL en frontend/.env
- Verificar CORS_ORIGINS en backend/.env

### Mercado Pago errores
- Verificar tokens (Production vs Test)
- Verificar montos sean válidos
- Revisar logs de webhook

## 📝 Próximos Pasos

1. ✅ Deployment en producción
2. ⬜ Agregar notificaciones por email
3. ⬜ App móvil (React Native)
4. ⬜ Sistema de calificaciones
5. ⬜ Chat en tiempo real
6. ⬜ Transferencias automáticas a profesionales

## 🤝 Soporte

Para dudas o problemas:
- 📧 Email: soporte@changared.com
- 📱 WhatsApp: +54 9 11 XXXX-XXXX

## 📄 Licencia

Copyright © 2026 ChangaRed. Todos los derechos reservados.

---

**Desarrollado con ❤️ usando IA y tecnologías modernas**
