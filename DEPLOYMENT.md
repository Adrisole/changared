# 📋 Guía Completa de Deployment - ChangaRed

## 🎯 ¿Qué es ChangaRed?

ChangaRed es una **aplicación full-stack** (NO es un plugin de WordPress):
- **Frontend**: React (interfaz de usuario)
- **Backend**: Python FastAPI (API y lógica)
- **Base de Datos**: MongoDB

## 🚀 Opciones de Deployment

### ⭐ OPCIÓN 1: Deployment con Vercel + Railway (RECOMENDADO - GRATIS)

Esta es la opción más fácil y gratuita para empezar.

#### A) Subir Frontend a Vercel (GRATIS)

1. **Crea cuenta en https://vercel.com** (gratis)

2. **Conecta tu código:**
   - Sube tu código a GitHub
   - En Vercel: "New Project" → Importa tu repositorio
   - Selecciona carpeta: `/app/frontend`

3. **Configura Variables de Entorno:**
   ```
   REACT_APP_BACKEND_URL = https://tu-backend.railway.app
   REACT_APP_MERCADOPAGO_PUBLIC_KEY = TEST-a8d1c033-6691-4e93-9e5c-37237da0fad4
   ```

4. **Deploy:** Vercel lo hace automático

5. **Tu frontend estará en:** `https://tu-app.vercel.app`

#### B) Subir Backend a Railway (GRATIS - 500 horas/mes)

1. **Crea cuenta en https://railway.app** (gratis)

2. **Nuevo Proyecto:**
   - "New Project" → "Deploy from GitHub repo"
   - Selecciona carpeta: `/app/backend`

3. **Configura Variables de Entorno:**
   ```
   MONGO_URL = tu-url-de-mongodb-atlas
   DB_NAME = changared_prod
   CORS_ORIGINS = https://tu-app.vercel.app
   EMERGENT_LLM_KEY = sk-emergent-15f4145Dc92Ee013f7
   JWT_SECRET = tu-clave-secreta-cambiala
   JWT_ALGORITHM = HS256
   JWT_EXPIRATION_MINUTES = 43200
   MERCADOPAGO_ACCESS_TOKEN = APP_USR-1167673738012793-032317-e08982a1e2ed6cbce2ec5e426199d967-92578531
   MERCADOPAGO_PUBLIC_KEY = (tu clave pública de producción)
   ```

4. **Agregar MongoDB:**
   - En Railway: "New" → "Database" → "MongoDB"
   - O usa MongoDB Atlas (gratis): https://mongodb.com/atlas

5. **Deploy:** Railway lo hace automático

6. **Tu backend estará en:** `https://tu-backend.railway.app`

---

### 🌐 OPCIÓN 2: Usar con tu Dominio y WordPress

#### Configuración A: Subdominio (RECOMENDADO)

```
Tu WordPress:     www.tudominio.com
Tu ChangaRed:     app.tudominio.com
```

**Pasos:**

1. **Deploya en Vercel + Railway** (Opción 1)

2. **Configura DNS en tu hosting:**
   - Tipo: CNAME
   - Nombre: `app`
   - Valor: `cname.vercel-dns.com`

3. **En Vercel:**
   - Settings → Domains
   - Add Domain: `app.tudominio.com`

4. **Integra en WordPress:**
   - Agrega un botón en tu menú que lleve a `app.tudominio.com`
   - O usa un iframe (no recomendado):
   ```html
   <iframe src="https://app.tudominio.com" width="100%" height="800px"></iframe>
   ```

#### Configuración B: Carpeta

```
Tu WordPress:     www.tudominio.com
Tu ChangaRed:     www.tudominio.com/app
```

Esto requiere configuración de proxy en tu servidor (más complejo).

---

### 🔧 OPCIÓN 3: VPS Propio (Digital Ocean, Linode, etc.)

Si tienes un VPS con control total:

#### Requisitos:
- Ubuntu 20.04+
- Node.js 16+
- Python 3.9+
- MongoDB
- Nginx

#### Setup Rápido:

```bash
# 1. Instalar dependencias
sudo apt update
sudo apt install -y python3.9 python3-pip nodejs npm mongodb nginx

# 2. Clonar tu código
git clone tu-repo.git /var/www/changared

# 3. Backend
cd /var/www/changared/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear .env con tus variables
nano .env

# Ejecutar con gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000

# 4. Frontend
cd /var/www/changared/frontend
npm install
npm run build

# 5. Nginx config
sudo nano /etc/nginx/sites-available/changared
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name app.tudominio.com;

    # Frontend
    location / {
        root /var/www/changared/frontend/build;
        try_files $uri /index.html;
    }

    # Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Activar y reiniciar
sudo ln -s /etc/nginx/sites-available/changared /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 💳 Configurar Mercado Pago para Producción

### 1. Ir a tu cuenta de Mercado Pago

https://www.mercadopago.com.ar/developers/

### 2. Crear Aplicación

- "Tus integraciones" → "Crear aplicación"
- Nombre: ChangaRed
- Tipo: Pagos online

### 3. Obtener Credenciales de PRODUCCIÓN

```
Access Token (Producción): APP_USR-XXXXXXXX
Public Key (Producción): APP_USR-XXXXXXXX
```

### 4. Reemplazar en tus Variables de Entorno

**Backend (.env):**
```
MERCADOPAGO_ACCESS_TOKEN=APP_USR-tu-token-de-produccion
```

**Frontend (.env):**
```
REACT_APP_MERCADOPAGO_PUBLIC_KEY=APP_USR-tu-public-key-de-produccion
```

---

## 🔄 Cómo Cobrar tu Comisión del 20%

### Sistema Actual (Automático):

1. **Cliente paga $5000** → Va TODO a tu cuenta de Mercado Pago
2. **Sistema calcula:**
   - Comisión ChangaRed: $1000 (20%)
   - Para el profesional: $4000 (80%)
3. **Tú transfieres** al profesional desde tu cuenta de Mercado Pago

### Opciones para Transferir al Profesional:

#### A) Manual (Más Simple):
1. Ver en Dashboard Admin cuánto ganó cada profesional
2. Hacer transferencia bancaria o Mercado Pago manualmente

#### B) Automático con Mercado Pago:
```python
# Usar la API de Mercado Pago para transferir
import mercadopago
sdk = mercadopago.SDK("tu_access_token")

money_request = sdk.money_request().create({
    "amount": 4000,
    "email": "profesional@email.com"
})
```

---

## 📊 Checklist de Deployment

### Antes de Producción:

- [ ] Cambia JWT_SECRET por algo único
- [ ] Cambia tokens de Mercado Pago a PRODUCCIÓN
- [ ] Configura CORS_ORIGINS con tu dominio real
- [ ] Prueba pagos en modo TEST primero
- [ ] Configura SSL/HTTPS (Vercel lo hace gratis)
- [ ] Crea profesionales de prueba
- [ ] Prueba todo el flujo: registro → solicitud → pago

### Después de Deployment:

- [ ] Monitorea logs de errores
- [ ] Revisa pagos en panel de Mercado Pago
- [ ] Configura backups de MongoDB
- [ ] Agrega Google Analytics (opcional)

---

## 🆘 Troubleshooting Común

### Error: "Cannot connect to MongoDB"
- Verifica que MONGO_URL esté correcto
- Whitelist de IP en MongoDB Atlas

### Error: "CORS policy blocked"
- Agrega tu dominio a CORS_ORIGINS en backend

### Error: "Mercado Pago API error"
- Verifica que estés usando credenciales de PRODUCCIÓN
- Revisa que los montos sean válidos (> 0)

### Pagos no llegan
- Verifica webhook URL en preferencia
- Revisa logs de webhook en tu backend

---

## 📞 Próximos Pasos

1. **Deploy en Vercel + Railway** (5 minutos)
2. **Prueba con token TEST** de Mercado Pago
3. **Cuando funcione, cambia a PRODUCCIÓN**
4. **Conecta tu dominio**
5. **¡Empieza a recibir solicitudes!**

---

## 💡 Recursos Útiles

- Mercado Pago Docs: https://www.mercadopago.com.ar/developers/
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- MongoDB Atlas: https://mongodb.com/atlas

---

**¿Necesitas ayuda con algún paso específico?**
Responde con el número de opción que quieres seguir y te ayudo paso a paso.
