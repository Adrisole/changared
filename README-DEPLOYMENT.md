# 📦 ChangaRed - Paquete Completo para Deployment

## 🎯 ¿Qué incluye este paquete?

✅ Código completo del Frontend (React)
✅ Código completo del Backend (FastAPI + Python)
✅ Configuración de base de datos (MongoDB)
✅ Integración de IA (OpenAI GPT-4o-mini)
✅ Integración de Mercado Pago (PRODUCCIÓN configurada)
✅ Todos los archivos de configuración

---

## 📥 CÓMO DESCARGAR LA APLICACIÓN

### Opción 1: Desde Emergent (Recomendado)

Si estás usando Emergent AI:

1. **Ve al menú superior derecho** (icono de 3 puntos)
2. Click en **"Export"** o **"Download Project"**
3. Selecciona **"Download as ZIP"**
4. Guarda el archivo: `changared.zip`

### Opción 2: Desde el Sistema de Archivos

Si tienes acceso al servidor:

```bash
# Navega al directorio principal
cd /app

# Crear archivo ZIP
zip -r changared.zip . -x "*/node_modules/*" -x "*/.venv/*" -x "*/__pycache__/*"

# Descargar usando scp (desde tu computadora)
scp user@servidor:/app/changared.zip ~/Desktop/
```

### Opción 3: Git Clone (Si está en GitHub)

```bash
git clone https://github.com/tu-usuario/changared.git
cd changared
```

---

## 📂 Estructura del Proyecto Descargado

```
changared/
├── backend/                    # API FastAPI
│   ├── server.py              # Servidor principal
│   ├── mercadopago_routes.py  # Rutas de pago
│   ├── requirements.txt       # Dependencias Python
│   └── .env                   # Variables de entorno
│
├── frontend/                   # Interfaz React
│   ├── src/
│   │   ├── pages/             # Páginas principales
│   │   ├── components/        # Componentes UI
│   │   ├── contexts/          # Context API
│   │   └── App.js             # App principal
│   ├── package.json           # Dependencias Node
│   └── .env                   # Variables de entorno
│
├── DEPLOYMENT.md              # Guía de deployment
└── README.md                  # Esta guía
```

---

## 🚀 DEPLOYMENT PASO A PASO

### PASO 1: Preparar tu Computadora

#### En Windows:
1. Instala **Git**: https://git-scm.com/download/win
2. Instala **Node.js** (v16+): https://nodejs.org/
3. Crea cuenta en **Vercel**: https://vercel.com
4. Crea cuenta en **Railway**: https://railway.app

#### En Mac/Linux:
```bash
# Verificar que tienes Node.js
node --version  # Debe ser v16 o superior

# Verificar Git
git --version
```

---

### PASO 2: Subir Código a GitHub

#### 2.1 Crear Repositorio en GitHub

1. Ve a https://github.com
2. Click en **"New Repository"**
3. Nombre: `changared`
4. **Importante**: Marca como **PRIVADO** (para proteger tus credenciales)
5. Click en **"Create Repository"**

#### 2.2 Subir tu Código

```bash
# Descomprime changared.zip en tu computadora
cd /ruta/a/changared

# Inicializar Git
git init
git add .
git commit -m "Initial commit - ChangaRed MVP"

# Conectar con GitHub (usa la URL de tu repo)
git remote add origin https://github.com/TU-USUARIO/changared.git
git branch -M main
git push -u origin main
```

---

### PASO 3: Deploy Frontend en Vercel (GRATIS)

#### 3.1 Conectar con GitHub

1. Ve a https://vercel.com
2. Click en **"New Project"**
3. Click en **"Import Git Repository"**
4. Selecciona tu repositorio `changared`
5. Click en **"Import"**

#### 3.2 Configurar el Proyecto

En la pantalla de configuración:

**Framework Preset:** Create React App
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `build`

#### 3.3 Variables de Entorno

Click en **"Environment Variables"** y agrega:

```
REACT_APP_BACKEND_URL = https://changared-backend.up.railway.app
REACT_APP_MERCADOPAGO_PUBLIC_KEY = APP_USR-899fd2b7-44d1-4f70-bb31-b16f47790c72
```

⚠️ **IMPORTANTE**: Por ahora deja `REACT_APP_BACKEND_URL` vacío, lo completaremos después del PASO 4

#### 3.4 Deploy

1. Click en **"Deploy"**
2. Espera 2-3 minutos
3. ¡Tu frontend estará en: `https://changared-XXXX.vercel.app`!

---

### PASO 4: Deploy Backend en Railway (GRATIS)

#### 4.1 Crear Proyecto

1. Ve a https://railway.app
2. Click en **"Start a New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a GitHub
5. Selecciona tu repositorio `changared`

#### 4.2 Configurar el Servicio

1. Railway detectará automáticamente Python
2. Root Directory: Cambia a `/backend`
3. Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

#### 4.3 Agregar MongoDB

1. En tu proyecto de Railway, click en **"+ New"**
2. Selecciona **"Database"**
3. Elige **"MongoDB"**
4. Railway creará una base de datos automáticamente

#### 4.4 Variables de Entorno

En Settings → Variables, agrega:

```
MONGO_URL = [Railway te lo da automáticamente al crear MongoDB]
DB_NAME = changared_prod
CORS_ORIGINS = https://changared-XXXX.vercel.app
EMERGENT_LLM_KEY = sk-emergent-15f4145Dc92Ee013f7
JWT_SECRET = CAMBIA_ESTO_POR_ALGO_SUPER_SEGURO_Y_ALEATORIO
JWT_ALGORITHM = HS256
JWT_EXPIRATION_MINUTES = 43200
MERCADOPAGO_ACCESS_TOKEN = APP_USR-6019407805410866-021915-c2dd9fe3649d3565e8edc6f15e771a58-120074805
MERCADOPAGO_PUBLIC_KEY = APP_USR-899fd2b7-44d1-4f70-bb31-b16f47790c72
FRONTEND_URL = https://changared-XXXX.vercel.app
BACKEND_URL = https://changared-backend.up.railway.app
PORT = 8000
```

⚠️ **IMPORTANTE**: 
- Reemplaza `changared-XXXX.vercel.app` con tu URL real de Vercel
- Railway te dará la URL del backend automáticamente

#### 4.5 Deploy

1. Click en **"Deploy"**
2. Espera 3-5 minutos
3. Tu backend estará en: `https://changared-backend.up.railway.app`

---

### PASO 5: Conectar Frontend con Backend

#### 5.1 Actualizar Frontend en Vercel

1. Ve a tu proyecto en Vercel
2. Settings → Environment Variables
3. Edita `REACT_APP_BACKEND_URL`:
   ```
   REACT_APP_BACKEND_URL = https://changared-backend.up.railway.app
   ```
4. Click en **"Save"**
5. Ve a **Deployments** y haz click en **"Redeploy"**

#### 5.2 Actualizar CORS en Backend

1. Ve a tu proyecto en Railway
2. Variables → Edita `CORS_ORIGINS`:
   ```
   CORS_ORIGINS = https://changared-XXXX.vercel.app
   ```
3. Railway redeployará automáticamente

---

### PASO 6: Conectar tu Dominio (Opcional)

#### 6.1 Para el Frontend (Vercel)

1. En tu proyecto de Vercel, ve a **Settings → Domains**
2. Click en **"Add Domain"**
3. Ingresa: `app.tudominio.com`
4. Vercel te dará instrucciones para configurar DNS

#### 6.2 Configurar DNS en tu Hosting

En tu panel de hosting (donde tienes WordPress):

**Tipo:** CNAME
**Nombre:** app
**Valor:** cname.vercel-dns.com
**TTL:** 3600

Espera 10-30 minutos para que se propague.

---

## ✅ VERIFICACIÓN POST-DEPLOYMENT

### 1. Probar el Frontend

Abre en tu navegador:
```
https://changared-XXXX.vercel.app
```

Deberías ver:
- ✅ Landing page con logo de ChangaRed
- ✅ Botones "Solicitar Servicio" y "Soy Profesional"
- ✅ Sección de servicios

### 2. Probar el Backend

Abre en tu navegador:
```
https://changared-backend.up.railway.app/api/
```

Deberías ver:
```json
{
  "message": "ChangaRed API v1.0",
  "status": "operational"
}
```

### 3. Probar Registro

1. Click en **"Solicitar Servicio"**
2. Regístrate con un email de prueba
3. Deberías poder entrar al dashboard

### 4. Probar Solicitud de Servicio

1. En el dashboard, click **"Nueva Solicitud"**
2. Describe un problema: "Necesito un electricista"
3. Submit
4. Deberías ver el servicio asignado con el profesional

### 5. Probar Mercado Pago

1. En una solicitud, click **"Pagar Ahora"**
2. Deberías ser redirigido a Mercado Pago
3. Usa tarjeta de prueba:
   - Número: 5031 7557 3453 0604
   - CVC: 123
   - Vencimiento: 11/25

---

## 🐛 TROUBLESHOOTING COMÚN

### Error: "Cannot connect to backend"

**Solución:**
1. Verifica que `REACT_APP_BACKEND_URL` en Vercel esté correcto
2. Verifica que el backend esté running en Railway
3. Verifica logs en Railway

### Error: "CORS policy blocked"

**Solución:**
1. En Railway, verifica que `CORS_ORIGINS` tenga tu URL de Vercel
2. Redeploy el backend

### Error: "Cannot connect to MongoDB"

**Solución:**
1. En Railway, verifica que MongoDB esté running
2. Verifica que `MONGO_URL` esté correcto en variables

### Error: "Mercado Pago API error"

**Solución:**
1. Verifica que `MERCADOPAGO_ACCESS_TOKEN` sea de PRODUCCIÓN (no TEST)
2. Verifica que `FRONTEND_URL` y `BACKEND_URL` estén correctos

### Pagos no se procesan

**Solución:**
1. Verifica en Mercado Pago panel que la transacción aparezca
2. Revisa logs del webhook en Railway
3. Verifica que `notification_url` sea accesible públicamente

---

## 📊 MONITOREO POST-DEPLOYMENT

### Ver Logs en Railway

```bash
# En tu proyecto de Railway
1. Click en tu servicio backend
2. Ve a "Deployments" → Click en el último deploy
3. Ve a "View Logs"
```

### Ver Logs en Vercel

```bash
# En tu proyecto de Vercel
1. Ve a "Deployments"
2. Click en el último deployment
3. Click en "View Function Logs"
```

### Monitorear Pagos en Mercado Pago

```
https://www.mercadopago.com.ar/activities
```

---

## 🔐 SEGURIDAD POST-DEPLOYMENT

### ✅ Checklist de Seguridad

- [ ] JWT_SECRET cambiado por uno único y aleatorio
- [ ] Credenciales de Mercado Pago son de PRODUCCIÓN
- [ ] Repository de GitHub es PRIVADO
- [ ] No hay archivos .env en el repositorio
- [ ] CORS_ORIGINS no está en "*"
- [ ] MongoDB tiene usuario/contraseña (Railway lo hace automático)

---

## 💰 COSTOS MENSUALES

### Plan Gratuito:
- **Vercel**: Gratis hasta 100GB bandwidth
- **Railway**: $5 de crédito gratis al mes (500 horas de backend)
- **MongoDB en Railway**: Incluido en el plan gratuito
- **Mercado Pago**: Solo pagas comisiones por transacciones (aprox. 5%)

### Total: $0 - $5/mes dependiendo del tráfico

---

## 🎓 PRÓXIMOS PASOS

Una vez que tu app esté online:

### 1. Crear Profesionales de Prueba

Regístrate como admin y crea profesionales en diferentes ubicaciones.

### 2. Probar el Flujo Completo

1. Cliente se registra
2. Solicita un servicio
3. Paga con Mercado Pago
4. Admin ve la comisión

### 3. Promocionar

- Agrega un botón en tu WordPress que lleve a `app.tudominio.com`
- Comparte en redes sociales
- Agrega anuncios en Facebook/Instagram Ads

---

## 📞 SOPORTE

### Si algo no funciona:

1. **Revisa los logs** en Railway y Vercel
2. **Verifica las variables de entorno** (80% de los problemas)
3. **Prueba localmente** primero con `npm start` y `uvicorn server:app`

### Recursos Útiles:

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Mercado Pago Developers: https://www.mercadopago.com.ar/developers/
- MongoDB Atlas: https://www.mongodb.com/docs/atlas/

---

## 🎉 ¡FELICIDADES!

Ahora tienes ChangaRed corriendo en producción con:
✅ IA que asigna profesionales automáticamente
✅ Pagos reales con Mercado Pago
✅ Dashboard profesional
✅ Tu comisión del 20% automática

**¡Es hora de conseguir tus primeros clientes!** 🚀

---

**Versión:** 1.0.0  
**Última actualización:** Febrero 2026  
**Creado con:** Emergent AI
