#!/bin/bash

# Script para crear archivo ZIP de ChangaRed listo para deployment

echo "🚀 Creando paquete de ChangaRed para deployment..."

cd /app

# Crear directorio temporal
mkdir -p /tmp/changared-deploy

# Copiar archivos necesarios
echo "📦 Copiando archivos..."

# Backend
cp -r backend /tmp/changared-deploy/
rm -rf /tmp/changared-deploy/backend/__pycache__
rm -rf /tmp/changared-deploy/backend/.venv

# Frontend
cp -r frontend /tmp/changared-deploy/
rm -rf /tmp/changared-deploy/frontend/node_modules
rm -rf /tmp/changared-deploy/frontend/build

# Documentación
cp DEPLOYMENT.md /tmp/changared-deploy/
cp README-DEPLOYMENT.md /tmp/changared-deploy/README.md
cp design_guidelines.json /tmp/changared-deploy/

# Crear .gitignore
cat > /tmp/changared-deploy/.gitignore << 'EOF'
# Dependencies
node_modules/
.venv/
venv/

# Build files
build/
dist/
*.pyc
__pycache__/

# Environment files (NO subir a GitHub público)
.env
.env.local
.env.production

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF

# Crear archivo de configuración para Railway
cat > /tmp/changared-deploy/backend/railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Crear archivo de configuración para Vercel
cat > /tmp/changared-deploy/frontend/vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/favicon.ico",
      "dest": "/favicon.ico"
    },
    {
      "src": "/manifest.json",
      "dest": "/manifest.json"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
EOF

# Crear README rápido
cat > /tmp/changared-deploy/QUICK-START.md << 'EOF'
# 🚀 ChangaRed - Quick Start

## Archivos Incluidos

✅ `/backend` - API FastAPI + Python
✅ `/frontend` - React App
✅ `README.md` - Guía completa de deployment
✅ `DEPLOYMENT.md` - Instrucciones técnicas

## Deploy en 10 Minutos

### 1. Sube a GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU-USUARIO/changared.git
git push -u origin main
```

### 2. Deploy Frontend (Vercel)
- Ve a https://vercel.com
- Import GitHub repo
- Root: `frontend`
- Deploy

### 3. Deploy Backend (Railway)
- Ve a https://railway.app
- New Project → GitHub repo
- Root: `backend`
- Add MongoDB database
- Deploy

### 4. Configura Variables
Ver `README.md` para lista completa de variables de entorno.

## Credenciales Incluidas

✅ Mercado Pago (Producción) - Configurado
✅ OpenAI IA - Configurado con Emergent LLM Key
✅ JWT Secret - Cámbialo en producción

## Soporte

Lee `README.md` para guía paso a paso completa.
EOF

# Crear archivo ZIP
echo "🗜️  Comprimiendo archivos..."
cd /tmp
zip -r changared-deploy.zip changared-deploy -x "*/node_modules/*" -x "*/.venv/*" -x "*/__pycache__/*" > /dev/null

# Mover a /app
mv changared-deploy.zip /app/

# Limpiar
rm -rf /tmp/changared-deploy

echo "✅ ¡Listo! Archivo creado: /app/changared-deploy.zip"
echo ""
echo "📊 Tamaño del archivo:"
ls -lh /app/changared-deploy.zip | awk '{print $5}'
echo ""
echo "📥 Para descargar:"
echo "1. Usa el botón 'Export' en Emergent"
echo "2. O descarga directamente: /app/changared-deploy.zip"
