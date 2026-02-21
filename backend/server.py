from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import httpx
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from openai import AsyncOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ChangaRed API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URL = os.environ.get("MONGO_URL", "")
client = AsyncIOMotorClient(MONGO_URL)
db = client.changared

# Auth
SECRET_KEY = os.environ.get("SECRET_KEY", "changared-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# LLM
EMERGENT_API_KEY = os.environ.get("EMERGENT_API_KEY", "")

# Mercado Pago
MP_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "")
MP_PUBLIC_KEY = os.environ.get("MERCADOPAGO_PUBLIC_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_CHAT_ID = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "")

# Email
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

# ─── MODELOS ────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    nombre: str
    telefono: str
    email: EmailStr
    password: str
    rol: Literal["cliente", "profesional"]
    tipo_servicio: Optional[str] = None
    zona: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SolicitudCreate(BaseModel):
    mensaje: str
    zona: Optional[str] = "Posadas"
    urgente: bool = False

class AdminAccion(BaseModel):
    accion: Literal["aceptar", "rechazar"]
    profesional_id: Optional[str] = None

class SolicitudUpdate(BaseModel):
    estado: Optional[str] = None
    profesional_id: Optional[str] = None

class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    telefono: str
    email: str
    password_hash: str
    rol: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Profesional(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    nombre: str
    telefono: str
    email: str
    tipo_servicio: str
    latitud: float
    longitud: float
    disponible: bool = True
    tarifa_base: float = 15000.0
    calificacion: float = 5.0
    zona: Optional[str] = "Posadas"

class Solicitud(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cliente_id: str
    cliente_nombre: str
    cliente_telefono: str = ""
    cliente_email: str = ""
    mensaje: str
    servicio: str
    zona: str
    urgente: bool = False
    estado: str = "pendiente_admin"
    profesional_id: Optional[str] = None
    profesional_nombre: Optional[str] = None
    profesional_telefono: Optional[str] = None
    tarifa_estimada_min: Optional[float] = None
    tarifa_estimada_max: Optional[float] = None
    tarifa_final: Optional[float] = None
    pago_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ─── HELPERS AUTH ────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: str, rol: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "rol": rol, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ─── TELEGRAM ────────────────────────────────────────────────────────────────

async def notificar_telegram(mensaje: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        logger.warning("Telegram no configurado")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client_http:
            await client_http.post(url, json={
                "chat_id": TELEGRAM_ADMIN_CHAT_ID,
                "text": mensaje,
                "parse_mode": "HTML"
            })
        logger.info("Notificacion Telegram enviada")
    except Exception as e:
        logger.error(f"Error Telegram: {e}")

# ─── EMAIL ────────────────────────────────────────────────────────────────────

async def notificar_changarin_email(profesional_email: str, profesional_nombre: str, solicitud: dict):
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("Email SMTP no configurado - saltando notificacion")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"ChangaRed - Nuevo trabajo de {solicitud.get('servicio', '').upper()}"
        msg["From"] = SMTP_USER
        msg["To"] = profesional_email

        tarifa_min = solicitud.get("tarifa_estimada_min", 0)
        tarifa_max = solicitud.get("tarifa_estimada_max", 0)

        cuerpo = f"""
Hola {profesional_nombre}!

Tenes un nuevo trabajo asignado en ChangaRed:

Servicio: {solicitud.get('servicio', '').upper()}
Problema: {solicitud.get('mensaje', '')}
Zona: {solicitud.get('zona', '')}
{'*** URGENTE ***' if solicitud.get('urgente') else ''}

Cliente: {solicitud.get('cliente_nombre', '')}
Telefono: {solicitud.get('cliente_telefono', 'Ver en app')}

Tu pago: ${tarifa_min * 0.90:,.0f} - ${tarifa_max * 0.90:,.0f}

Saludos,
Equipo ChangaRed
        """
        msg.attach(MIMEText(cuerpo, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, profesional_email, msg.as_string())

        logger.info(f"Email enviado a {profesional_nombre} ({profesional_email})")
    except Exception as e:
        logger.error(f"Error enviando email: {e}")

# ─── MERCADO PAGO ─────────────────────────────────────────────────────────────

async def crear_preferencia_mp(solicitud_id: str, servicio: str, monto: float, cliente_email: str) -> dict:
    if not MP_ACCESS_TOKEN:
        logger.warning("MERCADOPAGO_ACCESS_TOKEN no configurado")
        return {"error": "Pago no configurado"}
    try:
        payload = {
            "items": [{
                "title": f"ChangaRed - {servicio.capitalize()}",
                "quantity": 1,
                "unit_price": float(monto),
                "currency_id": "ARS"
            }],
            "payer": {"email": cliente_email},
            "external_reference": solicitud_id,
            "back_urls": {
                "success": "https://changared.com/pago/exitoso",
                "failure": "https://changared.com/pago/fallido",
                "pending": "https://changared.com/pago/pendiente"
            },
            "auto_return": "approved"
        }
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                "https://api.mercadopago.com/checkout/preferences",
                json=payload,
                headers={
                    "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                }
            )
            data = response.json()
            return {
                "preference_id": data.get("id"),
                "init_point": data.get("init_point"),
                "sandbox_url": data.get("sandbox_init_point")
            }
    except Exception as e:
        logger.error(f"Error Mercado Pago: {e}")
        return {"error": str(e)}

# ─── IA ──────────────────────────────────────────────────────────────────────

def detectar_servicio_por_palabras(mensaje: str) -> str:
    mensaje_lower = mensaje.lower()
    keywords = {
        "electricista":               ["luz", "electricidad", "corto", "enchufe", "cable", "interruptor", "tomacorriente", "electricista", "fusible", "tablero"],
        "plomero":                    ["agua", "caño", "pérdida", "perdida", "canilla", "inodoro", "baño", "desagüe", "plomero", "tubería", "cañería", "pileta"],
        "gasista":                    ["gas", "garrafa", "calefón", "calefon", "estufa", "calefaccion", "gasista", "termotanque"],
        "pintor":                     ["pintura", "pintar", "pincel", "rodillo", "pintor", "empapelar"],
        "carpintero":                 ["madera", "mueble", "carpintero", "bisagra", "placard", "estante"],
        "limpieza":                   ["limpieza", "limpiar", "alfombra", "ordenar", "limpieza profunda", "mucama"],
        "jardinero":                  ["jardín", "jardin", "pasto", "plantas", "poda", "cortar pasto", "jardinero", "césped", "cesped"],
        "cerrajero":                  ["cerradura", "llave", "candado", "cerrajero", "trabada", "quede afuera"],
        "técnico aire acondicionado": ["aire acondicionado", "split", "no enfría el aire", "calor no baja", "refrigeración aire"],
        "técnico lavarropas":         ["lavarropas", "lavadora", "lavar ropa", "centrifuga", "centrifugado"],
        "técnico heladeras":          ["heladera", "freezer", "refrigerador", "no enfría", "no enfria", "heladera rota"],
        "técnico electrodomésticos":  ["electrodoméstico", "microondas", "horno", "licuadora", "batidora", "televisor", "tv roto", "pantalla"],
        "albañil":                    ["albañil", "albanil", "revoque", "cemento", "construcción", "rajadura", "grieta", "humedad", "pared rota"],
        "mudanza":                    ["mudanza", "mudar", "mover muebles", "flete", "transporte muebles"],
        "técnico general":            ["técnico", "tecnico", "reparación", "reparacion", "arreglo", "no funciona", "roto", "falla"],
    }
    for servicio, palabras in keywords.items():
        if any(p in mensaje_lower for p in palabras):
            return servicio
    return "técnico general"

async def clasificar_solicitud_ia(mensaje: str, zona: str) -> dict:
    try:
        client_ai = AsyncOpenAI(api_key=EMERGENT_API_KEY)
        response = await client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Eres un clasificador de servicios para ChangaRed, plataforma de servicios en Misiones, Argentina.

Dado un mensaje de cliente, devuelve SOLO un JSON válido con este formato exacto:
{
  "servicio": "tipo_de_servicio",
  "tarifa_min": 15000,
  "tarifa_max": 25000,
  "descripcion": "descripcion breve"
}

Servicios válidos: electricista, plomero, gasista, pintor, carpintero, limpieza, jardinero, cerrajero, técnico aire acondicionado, técnico lavarropas, técnico heladeras, técnico electrodomésticos, albañil, mudanza, técnico general
Tarifas en pesos argentinos para Misiones (rango típico 15000-50000).
NO incluyas texto adicional, SOLO el JSON."""
                },
                {
                    "role": "user",
                    "content": f"Clasificar: {mensaje} (zona: {zona})"
                }
            ]
        )
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Error IA: {e}")
        servicio = detectar_servicio_por_palabras(mensaje)
        return {
            "servicio": servicio,
            "tarifa_min": 15000,
            "tarifa_max": 25000,
            "descripcion": f"Servicio de {servicio}"
        }

# ─── RUTAS ───────────────────────────────────────────────────────────────────

router = APIRouter()

@router.post("/api/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(
        nombre=user_data.nombre,
        telefono=user_data.telefono,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        rol=user_data.rol
    )
    user_doc = user.model_dump()
    user_doc["created_at"] = user_doc["created_at"].isoformat()
    await db.users.insert_one(user_doc)

    if user_data.rol == "profesional":
        coordenadas_zona = {
            "Posadas":                (-27.3621, -55.8948),
            "Garupá":                 (-27.4833, -55.8167),
            "Candelaria":             (-27.4667, -55.7500),
            "Santa Ana":              (-27.3667, -55.5833),
            "San Ignacio":            (-27.2667, -55.5333),
            "Jardín América":         (-27.0333, -55.2333),
            "Oberá":                  (-27.4833, -55.1333),
            "Apóstoles":              (-27.9167, -55.7500),
            "Azara":                  (-28.0500, -55.6667),
            "San José":               (-27.7667, -55.7833),
            "Eldorado":               (-26.4000, -54.6333),
            "Puerto Iguazú":          (-25.5972, -54.5789),
            "Wanda":                  (-25.9667, -54.5667),
            "Montecarlo":             (-26.5667, -54.7500),
            "Puerto Rico":            (-26.8000, -55.0167),
            "Leandro N. Alem":        (-27.6000, -55.3333),
            "Campo Grande":           (-27.2167, -54.9667),
            "Aristóbulo del Valle":   (-27.1000, -54.9000),
            "San Vicente":            (-26.9667, -54.7333),
            "Bernardo de Irigoyen":   (-26.2667, -53.6500),
        }
        lat, lon = coordenadas_zona.get(user_data.zona, (-27.3621, -55.8948))

        profesional = Profesional(
            id=user.id,
            nombre=user_data.nombre,
            telefono=user_data.telefono,
            email=user_data.email,
            tipo_servicio=user_data.tipo_servicio or "técnico general",
            latitud=lat,
            longitud=lon,
            disponible=True,
            tarifa_base=15000.0,
            zona=user_data.zona or "Posadas"
        )
        prof_doc = profesional.model_dump()
        await db.profesionales.insert_one(prof_doc)
        logger.info(f"Profesional {user_data.nombre} registrado como {user_data.tipo_servicio} en {user_data.zona}")

    token = create_token(user.id, user.rol)
    return {
        "token": token,
        "user": {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol}
    }

@router.post("/api/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_token(user["id"], user["rol"])
    return {
        "token": token,
        "user": {"id": user["id"], "nombre": user["nombre"], "email": user["email"], "rol": user["rol"]}
    }

@router.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "nombre": current_user["nombre"],
        "email": current_user["email"],
        "rol": current_user["rol"]
    }

@router.post("/api/solicitudes")
async def crear_solicitud(solicitud_data: SolicitudCreate, current_user: dict = Depends(get_current_user)):
    if current_user["rol"] != "cliente":
        raise HTTPException(status_code=403, detail="Solo clientes pueden crear solicitudes")

    clasificacion = await clasificar_solicitud_ia(solicitud_data.mensaje, solicitud_data.zona)
    servicio_detectado = clasificacion.get("servicio", "técnico general")

    tarifa_min = clasificacion.get("tarifa_min", 15000)
    tarifa_max = clasificacion.get("tarifa_max", 25000)

    if solicitud_data.urgente:
        tarifa_min = round(tarifa_min * 1.30)
        tarifa_max = round(tarifa_max * 1.30)

    solicitud = Solicitud(
        cliente_id=current_user["id"],
        cliente_nombre=current_user["nombre"],
        cliente_telefono=current_user.get("telefono", ""),
        cliente_email=current_user.get("email", ""),
        mensaje=solicitud_data.mensaje,
        servicio=servicio_detectado,
        zona=solicitud_data.zona or "Posadas",
        urgente=solicitud_data.urgente,
        estado="pendiente_admin",
        tarifa_estimada_min=tarifa_min,
        tarifa_estimada_max=tarifa_max,
    )

    sol_doc = solicitud.model_dump()
    sol_doc["created_at"] = sol_doc["created_at"].isoformat()
    await db.solicitudes.insert_one(sol_doc)

    pago_prof_min = round(tarifa_min * 0.90)
    pago_prof_max = round(tarifa_max * 0.90)
    comision_min  = round(tarifa_min * 0.10)
    comision_max  = round(tarifa_max * 0.10)

    logger.info(
        f"Solicitud {solicitud.id} | {servicio_detectado} | urgente={solicitud_data.urgente} | "
        f"cliente ve: ${tarifa_min:,.0f}-${tarifa_max:,.0f} | "
        f"profesional recibe: ${pago_prof_min:,.0f}-${pago_prof_max:,.0f} | "
        f"comision: ${comision_min:,.0f}-${comision_max:,.0f}"
    )

    urgente_txt = " - URGENTE" if solicitud_data.urgente else ""
    lineas = [
        f"NUEVA SOLICITUD{urgente_txt} - ChangaRed",
        f"Servicio: {servicio_detectado.upper()}",
        f"Problema: {solicitud_data.mensaje}",
        f"Zona: {solicitud_data.zona}",
        "",
        f"Cliente: {current_user['nombre']}",
        f"Tel: {current_user.get('telefono', 'N/A')}",
        "",
        f"Precio acordado: ${pago_prof_min:,.0f} - ${pago_prof_max:,.0f}",
        "",
        f"ID: {solicitud.id}"
    ]
    await notificar_telegram("\n".join(lineas))

    return {
        "id": solicitud.id,
        "servicio": servicio_detectado,
        "descripcion": clasificacion.get("descripcion", ""),
        "urgente": solicitud_data.urgente,
        "estado": "pendiente_admin",
        "tarifa_estimada_min": tarifa_min,
        "tarifa_estimada_max": tarifa_max,
        "mensaje": "Solicitud enviada. Te notificaremos cuando un profesional acepte el trabajo."
    }

@router.put("/api/admin/solicitudes/{solicitud_id}/accion")
async def admin_accion_solicitud(solicitud_id: str, accion_data: AdminAccion, current_user: dict = Depends(get_current_user)):
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede realizar esta accion")

    solicitud = await db.solicitudes.find_one({"id": solicitud_id})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if accion_data.accion == "rechazar":
        await db.solicitudes.update_one({"id": solicitud_id}, {"$set": {"estado": "cancelado"}})
        return {"mensaje": "Solicitud rechazada"}

    profesional_doc = None
    if accion_data.profesional_id:
        profesional_doc = await db.profesionales.find_one({"id": accion_data.profesional_id})
    else:
        profesional_doc = await db.profesionales.find_one({"tipo_servicio": solicitud["servicio"], "disponible": True})
        if not profesional_doc:
            profesional_doc = await db.profesionales.find_one({"disponible": True})

    if not profesional_doc:
        raise HTTPException(status_code=404, detail="No hay profesionales disponibles")

    await db.solicitudes.update_one(
        {"id": solicitud_id},
        {"$set": {
            "estado": "esperando_pago",
            "profesional_id": profesional_doc["id"],
            "profesional_nombre": profesional_doc["nombre"],
            "profesional_telefono": profesional_doc.get("telefono", "")
        }}
    )

    await notificar_changarin_email(
        profesional_email=profesional_doc["email"],
        profesional_nombre=profesional_doc["nombre"],
        solicitud=solicitud
    )

    return {
        "mensaje": f"Asignado a {profesional_doc['nombre']}. Se notifico al profesional.",
        "profesional": profesional_doc["nombre"],
        "estado": "esperando_pago"
    }

@router.get("/api/solicitudes")
async def listar_solicitudes(current_user: dict = Depends(get_current_user)):
    if current_user["rol"] == "cliente":
        cursor = db.solicitudes.find({"cliente_id": current_user["id"]})
    elif current_user["rol"] == "profesional":
        cursor = db.solicitudes.find({"profesional_id": current_user["id"]})
    else:
        cursor = db.solicitudes.find({})
    solicitudes = []
    async for sol in cursor:
        sol.pop("_id", None)
        solicitudes.append(sol)
    return solicitudes

@router.put("/api/solicitudes/{solicitud_id}")
async def actualizar_solicitud(solicitud_id: str, update_data: SolicitudUpdate, current_user: dict = Depends(get_current_user)):
    solicitud = await db.solicitudes.find_one({"id": solicitud_id})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    await db.solicitudes.update_one({"id": solicitud_id}, {"$set": update_dict})
    return {"mensaje": "Solicitud actualizada"}

@router.get("/api/profesionales")
async def listar_profesionales(current_user: dict = Depends(get_current_user)):
    cursor = db.profesionales.find({})
    profesionales = []
    async for prof in cursor:
        prof.pop("_id", None)
        profesionales.append(prof)
    return profesionales

@router.put("/api/profesionales/disponibilidad")
async def actualizar_disponibilidad(disponible: bool, current_user: dict = Depends(get_current_user)):
    if current_user["rol"] != "profesional":
        raise HTTPException(status_code=403, detail="Solo profesionales")
    await db.profesionales.update_one({"id": current_user["id"]}, {"$set": {"disponible": disponible}})
    return {"mensaje": f"Disponibilidad actualizada a {disponible}"}

@router.post("/api/solicitudes/{solicitud_id}/pago")
async def iniciar_pago(solicitud_id: str, current_user: dict = Depends(get_current_user)):
    solicitud = await db.solicitudes.find_one({"id": solicitud_id})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud["cliente_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    monto = solicitud.get("tarifa_final") or solicitud.get("tarifa_estimada_max", 25000)
    return await crear_preferencia_mp(
        solicitud_id=solicitud_id,
        servicio=solicitud["servicio"],
        monto=monto,
        cliente_email=current_user["email"]
    )

@router.get("/api/health")
async def health():
    return {"status": "ok", "app": "ChangaRed API"}

@router.get("/")
async def root():
    return {"message": "ChangaRed API funcionando"}

app.include_router(router)
