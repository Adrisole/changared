from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import asyncio
from math import radians, cos, sin, asin, sqrt
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'changared_secret')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION = int(os.environ.get('JWT_EXPIRATION_MINUTES', 43200))

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    telefono: str
    rol: Literal["cliente", "profesional"] = "cliente"  # Admin removido por seguridad
    tipo_servicio: Optional[str] = None  # Requerido si es profesional
    zona: Optional[str] = "Posadas"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    nombre: str
    telefono: str
    rol: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenResponse(BaseModel):
    token: str
    user: User

class ProfesionalCreate(BaseModel):
    nombre: str
    telefono: str
    email: EmailStr
    tipo_servicio: Literal[
        "electricista", "plomero", "gasista", 
        "tecnico_lavarropas", "tecnico_tv", "tecnico_heladeras", "tecnico_aire",
        "limpieza", "fletes", "albanil", "jardinero_poda", "pintor", 
        "ninero_cuidador", "tapiceria", "herreria"
    ]
    latitud: float
    longitud: float
    disponible: bool = True
    tarifa_base: float = 15000.0

class Profesional(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    telefono: str
    email: str
    tipo_servicio: str
    latitud: float
    longitud: float
    disponible: bool
    tarifa_base: float
    total_servicios: int = 0
    total_ganado: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SolicitudCreate(BaseModel):
    mensaje_cliente: str
    latitud: float
    longitud: float
    urgencia: Literal["normal", "urgente"] = "normal"

class Solicitud(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cliente_id: str
    cliente_nombre: str
    mensaje_cliente: str
    servicio: str
    categoria_trabajo: str = "reparacion_simple"
    profesional_id: str
    profesional_nombre: str
    latitud_cliente: float
    longitud_cliente: float
    distancia_km: float
    precio_total: float
    comision_changared: float
    pago_profesional: float
    urgencia: str
    estado: str = "pendiente_confirmacion"  # pendiente_confirmacion, confirmado, rechazado, en_proceso, completado, cancelado
    estado_pago: str = "sin_pagar"
    mercadopago_preference_id: Optional[str] = None
    mercadopago_payment_id: Optional[str] = None
    mensaje_respuesta: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmado_at: Optional[datetime] = None
    rechazado_at: Optional[datetime] = None

class AdminMetrics(BaseModel):
    total_solicitudes: int
    solicitudes_completadas: int
    total_ingresos: float
    total_comisiones: float
    profesionales_activos: int

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token(user_id: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION)
    payload = {"user_id": user_id, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_data = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_data:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        if isinstance(user_data['created_at'], str):
            user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
        
        return User(**user_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two coordinates in km"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return round(km, 2)

async def enviar_notificacion_telegram(solicitud: dict):
    """Envía notificación de nueva solicitud al admin por Telegram"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
    
    if not token or not chat_id:
        logging.warning("Telegram no configurado")
        return
    
    try:
        # Lista de profesionales disponibles
        profesionales_text = ""
        if 'profesionales_disponibles' in solicitud and solicitud['profesionales_disponibles']:
            profesionales_text = "\n\n👷 **PROFESIONALES DISPONIBLES:**\n"
            for i, prof in enumerate(solicitud['profesionales_disponibles'][:5], 1):
                profesionales_text += f"{i}. {prof['nombre']} - {prof['distancia']} km\n"
        
        # Formatear mensaje
        mensaje = f"""🔔 **NUEVA SOLICITUD ChangaRed**

👤 **Cliente:** {solicitud['cliente_nombre']}
🔧 **Servicio:** {solicitud['servicio'].replace('_', ' ').title()}
📋 **Categoría:** {solicitud['categoria_trabajo'].replace('_', ' ').title()}

💬 **Descripción:**
_{solicitud['mensaje_cliente']}_

⚠️ **Urgencia:** {solicitud['urgencia'].upper()}
💰 **Precio total:** ${solicitud['precio_total']:,.0f}
💵 **Tu comisión:** ${solicitud['comision_changared']:,.0f}
💸 **Pago profesional:** ${solicitud['pago_profesional']:,.0f}
{profesionales_text}
📍 **Zona:** Lat: {solicitud['latitud_cliente']:.4f}, Lon: {solicitud['longitud_cliente']:.4f}

⚡ **ACCIÓN REQUERIDA:**
Entrá al dashboard admin para asignar profesional:
{os.environ.get('FRONTEND_URL')}/admin

⏰ {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} hs
━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Enviar mensaje
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=10.0)
            if response.status_code == 200:
                logging.info(f"Notificación Telegram enviada para solicitud {solicitud['id']}")
            else:
                logging.error(f"Error enviando Telegram: {response.text}")
                
    except Exception as e:
        logging.error(f"Error en notificación Telegram: {str(e)}")

# Tabla de precios por servicio y categoría (en ARS)
PRECIOS = {
    "electricista": {
        "visita": (8000, 15000),
        "reparacion_simple": (15000, 28000),
        "reparacion_media": (25000, 60000),
        "instalacion": (40000, 180000)
    },
    "plomero": {
        "visita": (15000, 22000),
        "reparacion_simple": (18000, 45000),
        "reparacion_media": (28000, 85000),
        "instalacion": (25000, 110000)
    },
    "gasista": {
        "visita": (20000, 40000),
        "reparacion_simple": (20000, 55000),
        "reparacion_media": (35000, 90000),
        "instalacion": (45000, 180000)
    },
    "tecnico_lavarropas": {
        "visita": (12000, 25000),
        "reparacion_simple": (20000, 55000),
        "reparacion_media": (40000, 160000),
        "instalacion": (0, 0)
    },
    "tecnico_tv": {
        "visita": (8000, 25000),
        "reparacion_simple": (15000, 50000),
        "reparacion_media": (50000, 180000),
        "instalacion": (0, 0)
    },
    "tecnico_heladeras": {
        "visita": (15000, 28000),
        "reparacion_simple": (20000, 65000),
        "reparacion_media": (30000, 120000),
        "instalacion": (0, 0)
    },
    "tecnico_aire": {
        "visita": (15000, 25000),
        "reparacion_simple": (25000, 70000),
        "reparacion_media": (45000, 130000),
        "instalacion": (70000, 180000)
    },
    "limpieza": {
        "visita": (3500, 5500),
        "reparacion_simple": (14000, 22000),
        "reparacion_media": (25000, 45000),
        "instalacion": (35000, 70000)
    },
    "fletes": {
        "visita": (15000, 25000),
        "reparacion_simple": (40000, 80000),
        "reparacion_media": (70000, 130000),
        "instalacion": (110000, 200000)
    },
    "albanil": {
        "visita": (14000, 20000),
        "reparacion_simple": (25000, 35000),
        "reparacion_media": (30000, 70000),
        "instalacion": (120000, 280000)
    },
    "jardinero_poda": {
        "visita": (10000, 18000),
        "reparacion_simple": (18000, 35000),
        "reparacion_media": (35000, 65000),
        "instalacion": (50000, 120000)
    },
    "pintor": {
        "visita": (24000, 31000),
        "reparacion_simple": (35000, 75000),
        "reparacion_media": (120000, 280000),
        "instalacion": (0, 0)
    },
    "ninero_cuidador": {
        "visita": (3500, 6000),
        "reparacion_simple": (15000, 28000),
        "reparacion_media": (28000, 50000),
        "instalacion": (35000, 60000)
    },
    "tapiceria": {
        "visita": (10000, 25000),
        "reparacion_simple": (15000, 70000),
        "reparacion_media": (60000, 180000),
        "instalacion": (0, 0)
    },
    "herreria": {
        "visita": (20000, 45000),
        "reparacion_simple": (25000, 55000),
        "reparacion_media": (80000, 180000),
        "instalacion": (150000, 350000)
    }
}

def calcular_precio_servicio(tipo_servicio: str, categoria: str, urgente: bool = False) -> tuple:
    """Calcula precio según servicio, categoría y urgencia"""
    precios = PRECIOS.get(tipo_servicio, {}).get(categoria, (15000, 25000))
    min_precio, max_precio = precios
    
    if urgente:
        min_precio = int(min_precio * 1.3)
        max_precio = int(max_precio * 1.3)
    
    # Retornar precio promedio
    precio_promedio = (min_precio + max_precio) / 2
    return precio_promedio, min_precio, max_precio

def detectar_servicio_por_palabras(mensaje: str) -> str:
    """Detecta el servicio por palabras clave como fallback"""
    mensaje_lower = mensaje.lower()
    
    # Mapeo de palabras clave a servicios
    keywords = {
        "limpieza": ["limpieza", "limpiar", "alfombra", "tapizado", "mucama", "empleada doméstica", "barrer", "trapear"],
        "electricista": ["luz", "electricidad", "enchufe", "cable", "térmica", "tablero", "cortocircuito"],
        "plomero": ["agua", "caño", "cañería", "pérdida", "fuga", "inodoro", "canilla", "grifo", "baño", "ducha"],
        "gasista": ["gas", "garrafa", "calefón a gas", "estufa", "cocina a gas"],
        "tecnico_lavarropas": ["lavarropas", "lavadora", "secarropas", "centrifugado"],
        "tecnico_tv": ["televisor", "tv", "pantalla", "smart tv", "led"],
        "tecnico_heladeras": ["heladera", "freezer", "refrigerador", "no enfría"],
        "tecnico_aire": ["aire acondicionado", "split", "climatización"],
        "fletes": ["flete", "mudanza", "transporte", "traslado", "muebles"],
        "albanil": ["pared", "revoque", "yeso", "durlock", "cerámica", "grieta", "humedad"],
        "jardinero_poda": ["jardín", "pasto", "podar", "árboles", "plantas", "césped"],
        "pintor": ["pintar", "pintura", "latex", "esmalte"],
        "ninero_cuidador": ["niñero", "niñera", "cuidador", "bebé", "adulto mayor"],
        "tapiceria": ["tapizado", "sillón", "sofá", "retapizar"],
        "herreria": ["reja", "portón", "hierro", "soldadura", "parrilla"]
    }
    
    for servicio, palabras in keywords.items():
        for palabra in palabras:
            if palabra in mensaje_lower:
                return servicio
    
    return "electricista"  # Default

async def procesar_solicitud_con_ia(mensaje: str, lat: float, lon: float, urgencia: str, cliente_nombre: str):
    """Procesa solicitud usando IA y asigna profesional"""
    # Obtener todos los profesionales disponibles
    profesionales = await db.profesionales.find({"disponible": True}, {"_id": 0}).to_list(100)
    
    if not profesionales:
        raise HTTPException(status_code=404, detail="No hay profesionales disponibles")
    
    # Calcular distancias
    for prof in profesionales:
        prof['distancia'] = haversine(lon, lat, prof['longitud'], prof['latitud'])
    
    # Crear contexto para IA
    profesionales_info = "\n".join([
        f"{i+1}. {p['tipo_servicio'].replace('_', ' ').capitalize()} {p['id'][:8]}, a {p['distancia']} km"
        for i, p in enumerate(profesionales)
    ])
    
    prompt = f"""
Recibiste un mensaje de cliente: '{mensaje}'. 
Nombre del cliente: {cliente_nombre}
La ubicación del cliente es {lat},{lon}. 
La urgencia del servicio es '{urgencia}' (normal o urgente). 
Dispones de los siguientes profesionales:
{profesionales_info}

SERVICIOS DISPONIBLES CON PALABRAS CLAVE:
- electricista: luz, electricidad, corte de luz, cables, enchufe, térmica, tablero, instalación eléctrica, cortocircuito, aire acondicionado eléctrico
- plomero: agua, caño, cañería, pérdida, fuga, destapación, inodoro, canilla, grifo, pileta, baño, ducha, calefón, termotanque
- gasista: gas, calefón a gas, cocina, garrafa, habilitación de gas, calefacción, estufa
- tecnico_lavarropas: lavarropas, lavaropa, lavadora, secarropas, centrifugado, tambor
- tecnico_tv: televisor, TV, pantalla, smart tv, LED, plasma, monitor
- tecnico_heladeras: heladera, heladera, freezer, refrigerador, no enfría, hielo
- tecnico_aire: aire acondicionado, split, frío, calor, climatización, service de aire
- limpieza: limpieza, limpiar, lavar, barrer, trapear, ordenar, desinfectar, alfombra, tapizado de alfombra, limpieza profunda, mucama, empleada doméstica
- fletes: flete, mudanza, transporte, traslado, llevar muebles, camión, camioneta
- albanil: pared, mampostería, revoque, yeso, durlock, cerámica, porcelanato, grieta, humedad, construcción
- jardinero_poda: jardín, pasto, cortar pasto, podar, árboles, plantas, césped, desmalezar
- pintor: pintar, pintura, latex, esmalte, pared pintada, cambiar color
- ninero_cuidador: niñero, niñera, cuidado de niños, cuidar bebé, cuidador, adulto mayor, acompañante
- tapiceria: tapizado, sillón, sofá, mueble tapizado, retapizar, cambiar tela
- herreria: reja, portón, hierro, soldadura, parrilla, escalera de hierro

CATEGORÍAS DE TRABAJO:
- visita: solo revisión, diagnóstico, presupuesto, mirar, ver qué tiene
- reparacion_simple: trabajos de 30-60 min, cambios simples, ajustes menores
- reparacion_media: trabajos de 1-2 horas, reparaciones complejas
- instalacion: instalaciones nuevas o completas, trabajos grandes

EJEMPLOS CORRECTOS:
- "limpieza de alfombra" → servicio: limpieza, categoría: reparacion_simple
- "se me cortó la luz" → servicio: electricista, categoría: reparacion_simple
- "pérdida de agua en el baño" → servicio: plomero, categoría: reparacion_simple
- "necesito pintar mi casa" → servicio: pintor, categoría: reparacion_media
- "mudanza de 2 ambientes" → servicio: fletes, categoría: reparacion_media
- "cortar el pasto del jardín" → servicio: jardinero_poda, categoría: reparacion_simple

INSTRUCCIONES CRÍTICAS:
1. Lee CUIDADOSAMENTE el mensaje del cliente
2. Identifica las PALABRAS CLAVE del mensaje
3. Busca el servicio que MEJOR coincida con esas palabras
4. Si dice "limpieza" o "alfombra" → ES LIMPIEZA, NO gasista ni otro
5. Si dice "mudanza" o "flete" → ES FLETES, NO otra cosa
6. Determina la categoría según la complejidad descrita

RANGOS DE PRECIOS POR CATEGORÍA (en ARS):
Electricista: Visita 8k-15k | Simple 15k-28k | Media 25k-60k | Instalación 40k-180k
Plomero: Visita 15k-22k | Simple 18k-45k | Media 28k-85k | Instalación 25k-110k
Gasista: Visita 20k-40k | Simple 20k-55k | Media 35k-90k | Instalación 45k-180k
Técnico Lavarropas: Visita 12k-25k | Simple 20k-55k | Media 40k-160k
Técnico TV: Visita 8k-25k | Simple 15k-50k | Media 50k-180k
Técnico Heladeras: Visita 15k-28k | Simple 20k-65k | Media 30k-120k
Técnico Aire: Visita 15k-25k | Simple 25k-70k | Media 45k-130k | Instalación 70k-180k
Limpieza: Visita 3.5k-5.5k/h | Simple 14k-22k | Media 25k-45k | Instalación 35k-70k
Fletes: Visita 15k-25k | Simple 40k-80k | Media 70k-130k | Instalación 110k-200k
Albañil: Visita 14k-20k | Simple 25k-35k | Media 30k-70k | Instalación 120k-280k
Jardinero: Visita 10k-18k | Simple 18k-35k | Media 35k-65k | Instalación 50k-120k
Pintor: Visita 24k-31k | Simple 35k-75k | Media 120k-280k
Niñero: Visita 3.5k-6k/h | Simple 15k-28k | Media 28k-50k | Instalación 35k-60k
Tapicería: Visita 10k-25k | Simple 15k-70k | Media 60k-180k
Herrería: Visita 20k-45k | Simple 25k-55k | Media 80k-180k | Instalación 150k-350k

Tareas:
1. LEER el mensaje del cliente CON ATENCIÓN
2. IDENTIFICAR palabras clave específicas
3. DETERMINAR el servicio correcto (uno de los listados arriba)
4. DETERMINAR la categoría de trabajo según la descripción
5. Seleccionar el profesional más cercano disponible del tipo requerido
6. Calcular precio según categoría y aplicar +30% si es urgente
7. Calcular comisión de ChangaRed (20% del precio final)
8. Calcular pago al profesional (80% del precio final)
9. Generar mensaje profesional para el cliente incluyendo tipo de trabajo y rango de precio

Devuelve SOLO JSON válido con este formato exacto:
{{
  "servicio": "tipo de servicio detectado",
  "categoria_trabajo": "categoria detectada",
  "profesional_id": "ID del profesional",
  "precio_minimo": 0,
  "precio_maximo": 0,
  "precio_total": 0,
  "comision_changared": 0,
  "pago_profesional": 0,
  "mensaje_cliente": "mensaje amigable explicando servicio y precio",
  "resumen_admin": "resumen breve"
}}
"""
    
    try:
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"changared_{uuid.uuid4()}",
            system_message="Eres el asistente de ChangaRed. Respondes SOLO con JSON válido, sin texto adicional."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Limpiar respuesta
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        resultado = json.loads(response_text)
        
        # IMPORTANTE: Guardar el servicio detectado por la IA antes de buscar profesional
        servicio_detectado = resultado['servicio'].lower().replace(" ", "_")
        categoria = resultado.get('categoria_trabajo', 'reparacion_simple')
        
        # Encontrar profesional asignado
        profesional_asignado = None
        for prof in profesionales:
            if resultado.get('profesional_id') and resultado['profesional_id'] in prof['id']:
                profesional_asignado = prof
                break
        
        if not profesional_asignado:
            # Buscar el más cercano del tipo detectado por la IA
            candidatos = [p for p in profesionales if servicio_detectado in p['tipo_servicio']]
            if candidatos:
                profesional_asignado = min(candidatos, key=lambda x: x['distancia'])
            else:
                # No hay profesional del tipo requerido - usar el más cercano como fallback
                profesional_asignado = min(profesionales, key=lambda x: x['distancia'])
                logging.warning(f"No hay profesional de tipo '{servicio_detectado}', usando fallback")
        
        # Calcular precio basado en el SERVICIO DETECTADO (no el del profesional)
        precio_promedio, precio_min, precio_max = calcular_precio_servicio(
            servicio_detectado,  # Usar el servicio detectado, no el del profesional
            categoria,
            urgencia == "urgente"
        )
        
        comision = precio_promedio * 0.2
        pago = precio_promedio * 0.8
        
        resultado['profesional'] = profesional_asignado
        resultado['precio_total'] = precio_promedio
        resultado['precio_minimo'] = precio_min
        resultado['precio_maximo'] = precio_max
        resultado['comision_changared'] = comision
        resultado['pago_profesional'] = pago
        resultado['categoria_trabajo'] = categoria
        # CRÍTICO: Mantener el servicio detectado por la IA, NO sobrescribir
        resultado['servicio'] = servicio_detectado
        
        return resultado
        
    except Exception as e:
        logging.error(f"Error en IA: {str(e)}")
        # Fallback: detectar servicio por palabras clave
        servicio_fallback = detectar_servicio_por_palabras(mensaje)
        logging.info(f"Usando detección por palabras clave: {servicio_fallback}")
        
        # Buscar profesional del tipo detectado, si no hay usar el más cercano
        candidatos = [p for p in profesionales if servicio_fallback in p['tipo_servicio']]
        if candidatos:
            prof_cercano = min(candidatos, key=lambda x: x['distancia'])
        else:
            prof_cercano = min(profesionales, key=lambda x: x['distancia'])
        
        # Usar el precio del servicio detectado, no del profesional
        precio_promedio, precio_min, precio_max = calcular_precio_servicio(
            servicio_fallback,
            'reparacion_simple',
            urgencia == "urgente"
        )
        comision = precio_promedio * 0.2
        pago = precio_promedio * 0.8
        
        return {
            "servicio": servicio_fallback,
            "categoria_trabajo": "reparacion_simple",
            "profesional_id": prof_cercano['id'],
            "profesional": prof_cercano,
            "precio_minimo": precio_min,
            "precio_maximo": precio_max,
            "precio_total": precio_promedio,
            "comision_changared": comision,
            "pago_profesional": pago,
            "mensaje_cliente": f"Hola {cliente_nombre}, hemos recibido tu solicitud de {servicio_fallback.replace('_', ' ')}. Precio estimado: ${precio_min:,.0f} - ${precio_max:,.0f}. Te contactaremos pronto.",
            "resumen_admin": f"Solicitud procesada con detección por palabras clave"
        }

# Auth endpoints
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed_pw = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        nombre=user_data.nombre,
        telefono=user_data.telefono,
        rol=user_data.rol
    )
    
    doc = user.model_dump()
    doc['password'] = hashed_pw
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    token = create_token(user.id)
    
    return TokenResponse(token=token, user=user)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user_data = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_data:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not verify_password(credentials.password, user_data['password']):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if isinstance(user_data['created_at'], str):
        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
    
    user = User(**{k: v for k, v in user_data.items() if k != 'password'})
    token = create_token(user.id)
    
    return TokenResponse(token=token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Profesionales endpoints
@api_router.get("/profesionales", response_model=List[Profesional])
async def get_profesionales(current_user: User = Depends(get_current_user)):
    profesionales = await db.profesionales.find({}, {"_id": 0}).to_list(1000)
    for prof in profesionales:
        if isinstance(prof.get('created_at'), str):
            prof['created_at'] = datetime.fromisoformat(prof['created_at'])
    return profesionales

@api_router.post("/profesionales", response_model=Profesional)
async def create_profesional(prof_data: ProfesionalCreate, current_user: User = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    profesional = Profesional(**prof_data.model_dump())
    doc = profesional.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.profesionales.insert_one(doc)
    return profesional

@api_router.put("/profesionales/{prof_id}", response_model=Profesional)
async def update_profesional(prof_id: str, prof_data: ProfesionalCreate, current_user: User = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    update_data = prof_data.model_dump()
    result = await db.profesionales.update_one(
        {"id": prof_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    updated = await db.profesionales.find_one({"id": prof_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return Profesional(**updated)

@api_router.delete("/profesionales/{prof_id}")
async def delete_profesional(prof_id: str, current_user: User = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    result = await db.profesionales.delete_one({"id": prof_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    return {"message": "Profesional eliminado"}

# Solicitudes endpoints
@api_router.post("/solicitudes", response_model=Solicitud)
async def create_solicitud(solicitud_data: SolicitudCreate, current_user: User = Depends(get_current_user)):
    # Procesar con IA para detectar tipo de servicio y calcular precio
    resultado_ia = await procesar_solicitud_con_ia(
        solicitud_data.mensaje_cliente,
        solicitud_data.latitud,
        solicitud_data.longitud,
        solicitud_data.urgencia,
        current_user.nombre
    )
    
    profesional = resultado_ia['profesional']
    distancia = haversine(
        solicitud_data.longitud,
        solicitud_data.latitud,
        profesional['longitud'],
        profesional['latitud']
    )
    
    # Crear solicitud SIN asignar profesional aún (solo como sugerencia)
    solicitud = Solicitud(
        cliente_id=current_user.id,
        cliente_nombre=current_user.nombre,
        mensaje_cliente=solicitud_data.mensaje_cliente,
        servicio=resultado_ia['servicio'],
        categoria_trabajo=resultado_ia.get('categoria_trabajo', 'reparacion_simple'),
        profesional_id="",  # Sin asignar aún
        profesional_nombre="Pendiente asignación",
        latitud_cliente=solicitud_data.latitud,
        longitud_cliente=solicitud_data.longitud,
        distancia_km=distancia,
        precio_total=float(resultado_ia['precio_total']),
        comision_changared=float(resultado_ia['comision_changared']),
        pago_profesional=float(resultado_ia['pago_profesional']),
        urgencia=solicitud_data.urgencia,
        estado="pendiente_asignacion_admin",
        mensaje_respuesta=resultado_ia['mensaje_cliente']
    )
    
    doc = solicitud.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    # Guardar profesional sugerido en metadata
    doc['profesional_sugerido_id'] = profesional['id']
    doc['profesional_sugerido_nombre'] = profesional['nombre']
    
    await db.solicitudes.insert_one(doc)
    
    # Enviar notificación por Telegram al admin CON LISTA DE PROFESIONALES
    try:
        # Obtener profesionales disponibles del mismo tipo
        profesionales_disponibles = await db.profesionales.find({
            "tipo_servicio": resultado_ia['servicio'],
            "disponible": True
        }, {"_id": 0}).to_list(10)
        
        # Calcular distancias
        for prof in profesionales_disponibles:
            prof['distancia'] = haversine(
                solicitud_data.longitud,
                solicitud_data.latitud,
                prof['longitud'],
                prof['latitud']
            )
        
        # Ordenar por distancia
        profesionales_disponibles.sort(key=lambda x: x['distancia'])
        
        doc['profesionales_disponibles'] = profesionales_disponibles[:5]  # Top 5
        await enviar_notificacion_telegram(doc)
    except Exception as e:
        logging.error(f"Error enviando notificación: {str(e)}")
    
    return solicitud

@api_router.get("/solicitudes", response_model=List[Solicitud])
async def get_solicitudes(current_user: User = Depends(get_current_user)):
    if current_user.rol == "admin":
        query = {}
    elif current_user.rol == "cliente":
        query = {"cliente_id": current_user.id}
    else:
        # Obtener profesional_id del usuario
        prof = await db.profesionales.find_one({"email": current_user.email}, {"_id": 0})
        if prof:
            query = {"profesional_id": prof['id']}
        else:
            query = {"profesional_id": "none"}
    
    solicitudes = await db.solicitudes.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for sol in solicitudes:
        if isinstance(sol.get('created_at'), str):
            sol['created_at'] = datetime.fromisoformat(sol['created_at'])
    return solicitudes

@api_router.get("/solicitudes/{solicitud_id}", response_model=Solicitud)
async def get_solicitud(solicitud_id: str, current_user: User = Depends(get_current_user)):
    solicitud = await db.solicitudes.find_one({"id": solicitud_id}, {"_id": 0})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    if isinstance(solicitud.get('created_at'), str):
        solicitud['created_at'] = datetime.fromisoformat(solicitud['created_at'])
    
    return Solicitud(**solicitud)

@api_router.put("/solicitudes/{solicitud_id}/estado")
async def update_solicitud_estado(solicitud_id: str, estado: str, current_user: User = Depends(get_current_user)):
    result = await db.solicitudes.update_one(
        {"id": solicitud_id},
        {"$set": {"estado": estado}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    return {"message": "Estado actualizado"}

# Endpoints para profesionales
@api_router.post("/solicitudes/{solicitud_id}/aceptar")
async def aceptar_solicitud(solicitud_id: str, current_user: User = Depends(get_current_user)):
    """Profesional acepta la solicitud asignada"""
    # Buscar solicitud
    solicitud = await db.solicitudes.find_one({"id": solicitud_id}, {"_id": 0})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Verificar que es el profesional asignado
    profesional = await db.profesionales.find_one({"email": current_user.email}, {"_id": 0})
    if not profesional or profesional['id'] != solicitud['profesional_id']:
        raise HTTPException(status_code=403, detail="No eres el profesional asignado")
    
    # Verificar estado
    if solicitud['estado'] != 'pendiente_confirmacion':
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue procesada")
    
    # Actualizar a confirmado
    await db.solicitudes.update_one(
        {"id": solicitud_id},
        {
            "$set": {
                "estado": "confirmado",
                "confirmado_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": "Solicitud aceptada",
        "solicitud_id": solicitud_id,
        "cliente_nombre": solicitud['cliente_nombre']
    }

@api_router.post("/solicitudes/{solicitud_id}/rechazar")
async def rechazar_solicitud(solicitud_id: str, motivo: str = "", current_user: User = Depends(get_current_user)):
    """Profesional rechaza la solicitud - sistema busca otro"""
    # Buscar solicitud
    solicitud = await db.solicitudes.find_one({"id": solicitud_id}, {"_id": 0})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Verificar que es el profesional asignado
    profesional = await db.profesionales.find_one({"email": current_user.email}, {"_id": 0})
    if not profesional or profesional['id'] != solicitud['profesional_id']:
        raise HTTPException(status_code=403, detail="No eres el profesional asignado")
    
    # Verificar estado
    if solicitud['estado'] != 'pendiente_confirmacion':
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue procesada")
    
    # Marcar como rechazado por este profesional
    await db.solicitudes.update_one(
        {"id": solicitud_id},
        {
            "$set": {
                "rechazado_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "profesionales_rechazados": {
                    "profesional_id": profesional['id'],
                    "profesional_nombre": profesional['nombre'],
                    "motivo": motivo,
                    "rechazado_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    
    # Buscar siguiente profesional disponible
    profesionales_rechazados = solicitud.get('profesionales_rechazados', [])
    ids_rechazados = [p['profesional_id'] for p in profesionales_rechazados] + [profesional['id']]
    
    # Obtener profesionales del mismo tipo, disponibles y no rechazados
    profesionales_disponibles = await db.profesionales.find({
        "tipo_servicio": solicitud['servicio'],
        "disponible": True,
        "id": {"$nin": ids_rechazados}
    }, {"_id": 0}).to_list(100)
    
    if not profesionales_disponibles:
        # No hay más profesionales disponibles
        await db.solicitudes.update_one(
            {"id": solicitud_id},
            {"$set": {"estado": "sin_profesionales_disponibles"}}
        )
        return {
            "message": "Solicitud rechazada. No hay más profesionales disponibles.",
            "reasignado": False
        }
    
    # Calcular distancias y asignar al más cercano
    for prof in profesionales_disponibles:
        prof['distancia'] = haversine(
            solicitud['longitud_cliente'],
            solicitud['latitud_cliente'],
            prof['longitud'],
            prof['latitud']
        )
    
    nuevo_profesional = min(profesionales_disponibles, key=lambda x: x['distancia'])
    
    # Reasignar solicitud
    await db.solicitudes.update_one(
        {"id": solicitud_id},
        {
            "$set": {
                "profesional_id": nuevo_profesional['id'],
                "profesional_nombre": nuevo_profesional['nombre'],
                "distancia_km": nuevo_profesional['distancia'],
                "estado": "pendiente_confirmacion"
            }
        }
    )
    
    return {
        "message": "Solicitud rechazada y reasignada",
        "reasignado": True,
        "nuevo_profesional": nuevo_profesional['nombre']
    }

# Admin endpoints
@api_router.get("/admin/metrics", response_model=AdminMetrics)
async def get_admin_metrics(current_user: User = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    solicitudes = await db.solicitudes.find({}, {"_id": 0}).to_list(10000)
    profesionales = await db.profesionales.find({"disponible": True}, {"_id": 0}).to_list(1000)
    
    total_solicitudes = len(solicitudes)
    completadas = len([s for s in solicitudes if s.get('estado') == 'completado'])
    total_ingresos = sum(s.get('precio_total', 0) for s in solicitudes)
    total_comisiones = sum(s.get('comision_changared', 0) for s in solicitudes)
    
    return AdminMetrics(
        total_solicitudes=total_solicitudes,
        solicitudes_completadas=completadas,
        total_ingresos=total_ingresos,
        total_comisiones=total_comisiones,
        profesionales_activos=len(profesionales)
    )

@api_router.post("/admin/solicitudes/{solicitud_id}/asignar-profesional")
async def asignar_profesional_manual(
    solicitud_id: str, 
    profesional_id: str,
    current_user: User = Depends(get_current_user)
):
    """Admin asigna manualmente un profesional a la solicitud"""
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Buscar solicitud
    solicitud = await db.solicitudes.find_one({"id": solicitud_id}, {"_id": 0})
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Buscar profesional
    profesional = await db.profesionales.find_one({"id": profesional_id}, {"_id": 0})
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    
    # Calcular distancia
    distancia = haversine(
        solicitud['longitud_cliente'],
        solicitud['latitud_cliente'],
        profesional['longitud'],
        profesional['latitud']
    )
    
    # Asignar profesional
    await db.solicitudes.update_one(
        {"id": solicitud_id},
        {
            "$set": {
                "profesional_id": profesional['id'],
                "profesional_nombre": profesional['nombre'],
                "distancia_km": distancia,
                "estado": "pendiente_confirmacion",
                "asignado_manualmente_por": current_user.nombre,
                "asignado_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": f"Profesional {profesional['nombre']} asignado correctamente",
        "solicitud_id": solicitud_id,
        "profesional_id": profesional_id,
        "estado": "pendiente_confirmacion"
    }

# Test endpoint
@api_router.get("/")
async def root():
    return {"message": "ChangaRed API v1.0", "status": "operational"}

# Include Mercado Pago routes
from mercadopago_routes import router as mercadopago_router
app.include_router(mercadopago_router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()