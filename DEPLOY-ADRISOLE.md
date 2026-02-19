# 🚀 ChangaRed - Deployment en 15 Minutos

## ✅ Tu código ya está en GitHub!

**Repositorio:** https://github.com/Adrisole/changared

---

## 📋 PASO 1: Deploy Frontend en Vercel (5 min)

### 1.1 Ir a Vercel

1. Ve a: https://vercel.com/signup
2. Click en **"Continue with GitHub"**
3. Autoriza Vercel

### 1.2 Importar Proyecto

1. Click en **"Add New..."** → **"Project"**
2. Busca tu repo: **"changared"**
3. Click en **"Import"**

### 1.3 Configurar

**Framework Preset:** Create React App  
**Root Directory:** `frontend` ⚠️ IMPORTANTE  
**Build Command:** `yarn build`  
**Output Directory:** `build`

### 1.4 Variables de Entorno

Click en **"Environment Variables"** y agrega (déjalas así por ahora):

```
REACT_APP_BACKEND_URL = PENDIENTE
REACT_APP_MERCADOPAGO_PUBLIC_KEY = APP_USR-899fd2b7-44d1-4f70-bb31-b16f47790c72
```

### 1.5 Deploy

1. Click **"Deploy"**
2. Espera 2-3 minutos ☕
3. Guarda tu URL: `https://changared-XXXX.vercel.app`

---

## 📋 PASO 2: Deploy Backend en Railway (5 min)

### 2.1 Ir a Railway

1. Ve a: https://railway.app/new
2. Click en **"Login with GitHub"**
3. Autoriza Railway

### 2.2 Crear Proyecto

1. Click en **"Deploy from GitHub repo"**
2. Selecciona: **"Adrisole/changared"**
3. Click en **"Deploy Now"**

### 2.3 Configurar Root Directory

1. En Settings → busca **"Root Directory"**
2. Cambia a: `backend`
3. Save

### 2.4 Configurar Start Command

1. En Settings → busca **"Start Command"**
2. Cambia a: `uvicorn server:app --host 0.0.0.0 --port $PORT`
3. Save

### 2.5 Agregar MongoDB

1. En tu proyecto, click en **"+ New"**
2. Selecciona **"Database"**
3. Click en **"Add MongoDB"**
4. Railway lo configurará automáticamente

### 2.6 Variables de Entorno

En Settings → Variables, click **"+ New Variable"** para cada una:

```
MONGO_URL = mongodb://mongo:KLnJCKtxOFkxBVrTDcLFqoVBDxjQJnlG@mongodb.railway.internal:27017
DB_NAME = changared_prod
CORS_ORIGINS = https://changared-XXXX.vercel.app
EMERGENT_LLM_KEY = sk-emergent-15f4145Dc92Ee013f7
JWT_SECRET = changared_2026_super_secret_production_key_XYZ123
JWT_ALGORITHM = HS256
JWT_EXPIRATION_MINUTES = 43200
MERCADOPAGO_ACCESS_TOKEN = APP_USR-6019407805410866-021915-c2dd9fe3649d3565e8edc6f15e771a58-120074805
MERCADOPAGO_PUBLIC_KEY = APP_USR-899fd2b7-44d1-4f70-bb31-b16f47790c72
FRONTEND_URL = https://changared-XXXX.vercel.app
BACKEND_URL = https://changared-production.up.railway.app
PORT = 8000
```

⚠️ **IMPORTANTE:** 
- Railway te dará el `MONGO_URL` automáticamente al crear MongoDB
- Reemplaza `changared-XXXX.vercel.app` con tu URL REAL de Vercel

### 2.7 Deploy

Railway redeployará automáticamente. Espera 3-4 minutos.

Tu backend estará en: `https://changared-production.up.railway.app`

---

## 📋 PASO 3: Conectar Frontend con Backend (2 min)

### 3.1 Actualizar Vercel

1. Ve a tu proyecto en Vercel
2. Settings → Environment Variables
3. Edita `REACT_APP_BACKEND_URL`:
   ```
   REACT_APP_BACKEND_URL = https://changared-production.up.railway.app
   ```
4. **Save**
5. Ve a **Deployments** → Click en los 3 puntos → **"Redeploy"**

### 3.2 Actualizar Railway

1. Ve a tu proyecto en Railway
2. Variables → Edita `CORS_ORIGINS` y `FRONTEND_URL`:
   ```
   CORS_ORIGINS = https://changared-XXXX.vercel.app
   FRONTEND_URL = https://changared-XXXX.vercel.app
   ```
   (Usa tu URL REAL de Vercel)
3. Railway redeployará automáticamente

---

## ✅ PASO 4: Verificar que Funciona

### 4.1 Probar Frontend

Abre: `https://changared-XXXX.vercel.app`

Deberías ver:
- ✅ Landing page de ChangaRed
- ✅ Logo
- ✅ Botones funcionales

### 4.2 Probar Backend

Abre: `https://changared-production.up.railway.app/api/`

Deberías ver:
```json
{
  "message": "ChangaRed API v1.0",
  "status": "operational"
}
```

### 4.3 Probar Registro

1. En tu frontend, click **"Solicitar Servicio"**
2. Regístrate con tu email
3. Deberías entrar al dashboard

### 4.4 Crear Admin

1. Regístrate con rol **"Administrador"**
2. Entra al dashboard admin
3. Crea 2-3 profesionales de prueba

### 4.5 Probar Pago

1. Como cliente, crea una solicitud
2. Click **"Pagar Ahora"**
3. Deberías ir a Mercado Pago
4. Usa tarjeta de prueba:
   - **Número:** 5031 7557 3453 0604
   - **CVC:** 123
   - **Vencimiento:** 11/25

---

## 🌐 PASO 5 (Opcional): Conectar tu Dominio

### 5.1 Configurar DNS

En tu hosting de WordPress:

**Tipo:** CNAME  
**Nombre:** `app`  
**Valor:** `cname.vercel-dns.com`  
**TTL:** 3600

### 5.2 Agregar en Vercel

1. Settings → Domains
2. **"Add Domain"**
3. Ingresa: `app.tudominio.com`
4. Vercel verificará automáticamente

Espera 10-30 minutos para propagación DNS.

### 5.3 Actualizar Variables

Cuando funcione `app.tudominio.com`:

**En Railway:**
```
CORS_ORIGINS = https://app.tudominio.com
FRONTEND_URL = https://app.tudominio.com
```

**En Vercel:**
```
REACT_APP_BACKEND_URL = https://changared-production.up.railway.app
```
(el backend no cambia)

### 5.4 Agregar en WordPress

En tu menú de WordPress, agrega un botón que lleve a:
```
https://app.tudominio.com
```

O crea una página con iframe:
```html
<iframe src="https://app.tudominio.com" width="100%" height="800px" frameborder="0"></iframe>
```

---

## 💰 Costos Mensuales

**Vercel:** GRATIS (100GB bandwidth)  
**Railway:** $5 USD/mes (500 horas backend)  
**MongoDB:** Incluido en Railway  
**Mercado Pago:** 5% por transacción

**Total:** ~$5 USD/mes + comisiones MP

---

## 🐛 Si algo no funciona

### Frontend no carga
- Verifica que Root Directory sea `frontend`
- Revisa logs en Vercel

### Backend no responde
- Verifica que Root Directory sea `backend`
- Verifica que Start Command sea correcto
- Revisa logs en Railway

### Error CORS
- Verifica que `CORS_ORIGINS` tenga tu URL de Vercel EXACTA
- Redeploy backend

### MongoDB no conecta
- Verifica que Railway creó MongoDB
- Verifica que `MONGO_URL` esté en variables

### Pagos no funcionan
- Verifica que tokens de Mercado Pago sean de PRODUCCIÓN
- Verifica que `FRONTEND_URL` y `BACKEND_URL` estén correctos

---

## 📊 Monitorear tu App

### Ver Logs Backend (Railway)
1. Click en tu servicio
2. Ve a "Deployments"
3. Click en el último deploy
4. "View Logs"

### Ver Logs Frontend (Vercel)
1. Ve a "Deployments"
2. Click en el último
3. "View Function Logs"

### Ver Pagos (Mercado Pago)
https://www.mercadopago.com.ar/activities

---

## 🎉 ¡FELICIDADES!

Tu app ChangaRed está en producción con:
✅ IA que asigna profesionales
✅ Pagos reales con Mercado Pago
✅ Dashboard completo
✅ Tu comisión del 20% automática

**URL de tu app:** https://changared-XXXX.vercel.app  
**Repo GitHub:** https://github.com/Adrisole/changared

---

## 📞 Próximos Pasos

1. ✅ Crea profesionales de prueba
2. ✅ Prueba todo el flujo end-to-end
3. ✅ Conecta tu dominio
4. ✅ Promociona en redes sociales
5. ✅ ¡Consigue tus primeros clientes!

**¿Algún problema?** Revisa los logs y verifica las variables de entorno (80% de los problemas).

---

**Creado:** Febrero 2026  
**Por:** Emergent AI  
**Usuario:** @Adrisole
