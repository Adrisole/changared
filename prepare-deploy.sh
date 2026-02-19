#!/bin/bash

# 📦 Script para preparar ChangaRed para deployment
# Este script limpia y empaqueta todo lo necesario

echo "🚀 Preparando ChangaRed para deployment..."

# Crear directorio de distribución
mkdir -p /app/changared-deploy
cd /app/changared-deploy

# Copiar backend
echo "📁 Copiando backend..."
mkdir -p backend
cp -r /app/backend/*.py backend/
cp /app/backend/requirements.txt backend/
cp /app/backend/.env backend/.env.example

# Copiar frontend
echo "📁 Copiando frontend..."
mkdir -p frontend
cp -r /app/frontend/src frontend/
cp -r /app/frontend/public frontend/
cp /app/frontend/package.json frontend/
cp /app/frontend/tailwind.config.js frontend/
cp /app/frontend/postcss.config.js frontend/
cp /app/frontend/craco.config.js frontend/ 2>/dev/null || true
cp /app/frontend/.env frontend/.env.example

# Copiar documentación
echo "📄 Copiando documentación..."
cp /app/README.md .
cp /app/DEPLOYMENT.md .
cp /app/design_guidelines.json .

# Crear .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
venv/
__pycache__/
*.pyc
.Python

# Environment
.env
.env.local
.env.production

# Build
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
EOF

# Crear estructura completa
cat > ESTRUCTURA.md << 'EOF'
# 📁 Estructura de ChangaRed

```
changared/
├── backend/
│   ├── server.py                 # Servidor FastAPI principal
│   ├── mercadopago_routes.py     # Rutas de Mercado Pago
│   ├── requirements.txt          # Dependencias Python
│   └── .env.example             # Template de variables
│
├── frontend/
│   ├── public/                   # Archivos estáticos
│   ├── src/
│   │   ├── components/          # Componentes UI
│   │   │   ├── ui/             # Shadcn components
│   │   │   └── DashboardLayout.js
│   │   ├── contexts/
│   │   │   └── AuthContext.js   # Gestión de autenticación
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── AuthPage.js
│   │   │   ├── ClienteDashboard.js
│   │   │   └── AdminDashboard.js
│   │   ├── App.js               # App principal
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json             # Dependencias Node
│   ├── tailwind.config.js       # Config Tailwind
│   └── .env.example            # Template de variables
│
├── README.md                     # Documentación principal
├── DEPLOYMENT.md                 # Guía de deployment
├── design_guidelines.json        # Guía de diseño
└── .gitignore                   # Archivos a ignorar
```
EOF

# Crear guía de inicio rápido
cat > QUICKSTART.md << 'EOF'
# ⚡ Inicio Rápido - ChangaRed

## 🚀 Deployment en 10 Minutos

### Paso 1: Preparar Cuentas (Gratis)

1. **Vercel**: https://vercel.com/signup
2. **Railway**: https://railway.app
3. **MongoDB Atlas**: https://mongodb.com/cloud/atlas/register

### Paso 2: MongoDB Atlas

1. Crea cluster gratuito (M0)
2. Database Access → Add User (username/password)
3. Network Access → Add IP Address → Allow from anywhere (0.0.0.0/0)
4. Copia connection string:
   ```
   mongodb+srv://user:password@cluster.mongodb.net/changared
   ```

### Paso 3: Backend en Railway

```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Crear proyecto
cd backend
railway init

# 4. Agregar variables de entorno
railway variables set MONGO_URL="tu-mongodb-url"
railway variables set DB_NAME="changared"
railway variables set CORS_ORIGINS="*"
railway variables set EMERGENT_LLM_KEY="sk-emergent-15f4145Dc92Ee013f7"
railway variables set JWT_SECRET="cambia-esto-por-algo-unico"
railway variables set JWT_ALGORITHM="HS256"
railway variables set JWT_EXPIRATION_MINUTES="43200"
railway variables set MERCADOPAGO_ACCESS_TOKEN="APP_USR-6019407805410866-021915-c2dd9fe3649d3565e8edc6f15e771a58-120074805"

# 5. Deploy
railway up

# 6. Obtener URL
railway status
# Copia la URL, ejemplo: https://backend-production-xxxx.up.railway.app
```

### Paso 4: Frontend en Vercel

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy
cd ../frontend

# 4. Crear .env.production
cat > .env.production << EOF
REACT_APP_BACKEND_URL=https://tu-backend-railway.up.railway.app
REACT_APP_MERCADOPAGO_PUBLIC_KEY=APP_USR-899fd2b7-44d1-4f70-bb31-b16f47790c72
EOF

# 5. Deploy
vercel --prod

# Tu app estará en: https://tu-app.vercel.app
```

### Paso 5: Conectar tu Dominio (Opcional)

#### En Vercel:
1. Project Settings → Domains
2. Add: `app.tudominio.com`
3. Sigue instrucciones DNS

#### En tu hosting DNS:
```
Type: CNAME
Name: app
Value: cname.vercel-dns.com
```

### Paso 6: Configurar Webhooks de Mercado Pago

1. Ve a: https://www.mercadopago.com.ar/developers/panel
2. Tu aplicación → Webhooks
3. URL: `https://tu-backend-railway.up.railway.app/api/payments/webhook`
4. Eventos: Payments

### ✅ ¡Listo!

Tu app está online en:
- **Frontend**: https://tu-app.vercel.app
- **Backend**: https://tu-backend-railway.up.railway.app

### 🧪 Primer Login

1. Ve a tu frontend
2. Registrate como "admin"
3. Email: tu@email.com
4. Password: tu-password-seguro
5. ¡Empieza a agregar profesionales!

### 🆘 Problemas Comunes

**Error: Cannot connect to database**
→ Verifica MONGO_URL en Railway

**Error: CORS blocked**
→ Actualiza CORS_ORIGINS en Railway con tu URL de Vercel

**Error: Payment creation failed**
→ Verifica tokens de Mercado Pago

### 📞 Siguiente Paso

Lee `DEPLOYMENT.md` para opciones avanzadas y personalización.
EOF

echo "✅ ChangaRed preparado en: /app/changared-deploy"
echo ""
echo "📦 Contenido:"
ls -lah /app/changared-deploy
echo ""
echo "Para crear ZIP:"
echo "cd /app && tar -czf changared.tar.gz changared-deploy/"
