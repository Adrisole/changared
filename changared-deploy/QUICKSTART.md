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
