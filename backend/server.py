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
    rol: Literal["cliente", "profesional", "admin"] = "cliente"

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
    tipo_servicio: Literal["electricista", "plomero", "gasista", "tecnico_lavarropas", "tecnico_tv", "tecnico_heladeras", "tecnico_aire"]
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
    estado: str = "pendiente"
    estado_pago: str = "sin_pagar"
    mercadopago_preference_id: Optional[str] = None
    mercadopago_payment_id: Optional[str] = None
    mensaje_respuesta: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
        f"{i+1}. {p['tipo_servicio'].capitalize()} {p['id'][:8]}, a {p['distancia']} km, tarifa base ${p['tarifa_base']}"
        for i, p in enumerate(profesionales)
    ])
    
    prompt = f"""
Recibiste un mensaje de cliente: '{mensaje}'. 
Nombre del cliente: {cliente_nombre}
La ubicación del cliente es {lat},{lon}. 
La urgencia del servicio es '{urgencia}' (normal o urgente). 
Dispones de los siguientes profesionales:
{profesionales_info}

Tareas:
1. Determinar el tipo de servicio requerido (electricista, plomero, o gasista).
2. Seleccionar el profesional más cercano disponible del tipo requerido.
3. Estimar precio base según la tarifa del profesional y aplicar +30% si es urgente.
4. Calcular comisión de ChangaRed (20% del precio final).
5. Calcular pago al profesional (80% del precio final).
6. Generar mensaje profesional listo para enviar al cliente, incluyendo servicio, precio y confirmación.
7. Crear resumen para administración.

Devuelve SOLO JSON válido con este formato exacto:
{{
  "servicio": "tipo de servicio detectado",
  "profesional_id": "ID del profesional",
  "precio_base": 0,
  "precio_total": 0,
  "comision_changared": 0,
  "pago_profesional": 0,
  "mensaje_cliente": "mensaje amigable para el cliente",
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
        
        # Encontrar profesional asignado
        profesional_asignado = None
        for prof in profesionales:
            if resultado['profesional_id'] in prof['id']:
                profesional_asignado = prof
                break
        
        if not profesional_asignado:
            # Asignar el más cercano del tipo detectado
            tipo = resultado['servicio'].lower()
            candidatos = [p for p in profesionales if tipo in p['tipo_servicio']]
            if candidatos:
                profesional_asignado = min(candidatos, key=lambda x: x['distancia'])
            else:
                profesional_asignado = profesionales[0]
        
        resultado['profesional'] = profesional_asignado
        return resultado
        
    except Exception as e:
        logging.error(f"Error en IA: {str(e)}")
        # Fallback: asignar el profesional más cercano
        prof_cercano = min(profesionales, key=lambda x: x['distancia'])
        precio_base = prof_cercano['tarifa_base']
        precio_total = precio_base * 1.3 if urgencia == "urgente" else precio_base
        comision = precio_total * 0.2
        pago = precio_total * 0.8
        
        return {
            "servicio": prof_cercano['tipo_servicio'],
            "profesional_id": prof_cercano['id'],
            "profesional": prof_cercano,
            "precio_base": precio_base,
            "precio_total": precio_total,
            "comision_changared": comision,
            "pago_profesional": pago,
            "mensaje_cliente": f"Hola {cliente_nombre}, hemos asignado un {prof_cercano['tipo_servicio']} para tu solicitud. Precio: ${precio_total:.2f}. ¡Llegará pronto!",
            "resumen_admin": f"Solicitud procesada automáticamente (fallback)"
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
    # Procesar con IA
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
    
    solicitud = Solicitud(
        cliente_id=current_user.id,
        cliente_nombre=current_user.nombre,
        mensaje_cliente=solicitud_data.mensaje_cliente,
        servicio=resultado_ia['servicio'],
        profesional_id=profesional['id'],
        profesional_nombre=profesional['nombre'],
        latitud_cliente=solicitud_data.latitud,
        longitud_cliente=solicitud_data.longitud,
        distancia_km=distancia,
        precio_total=float(resultado_ia['precio_total']),
        comision_changared=float(resultado_ia['comision_changared']),
        pago_profesional=float(resultado_ia['pago_profesional']),
        urgencia=solicitud_data.urgencia,
        mensaje_respuesta=resultado_ia['mensaje_cliente']
    )
    
    doc = solicitud.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.solicitudes.insert_one(doc)
    
    # Actualizar estadísticas del profesional
    await db.profesionales.update_one(
        {"id": profesional['id']},
        {
            "$inc": {
                "total_servicios": 1,
                "total_ganado": solicitud.pago_profesional
            }
        }
    )
    
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