from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import mercadopago
import os
import logging
from datetime import datetime, timezone

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = logging.getLogger(__name__)

# Inicializar SDK de Mercado Pago
mp_access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
if not mp_access_token:
    logger.warning("MERCADOPAGO_ACCESS_TOKEN no configurado")
    sdk = None
else:
    sdk = mercadopago.SDK(mp_access_token)

class CreatePaymentRequest(BaseModel):
    solicitud_id: str
    cliente_email: EmailStr
    cliente_nombre: str
    monto_total: float
    descripcion: str
    
class PaymentPreferenceResponse(BaseModel):
    preference_id: str
    init_point: str
    sandbox_init_point: str
    monto_total: float
    comision_changared: float
    pago_profesional: float

@router.post("/create-preference", response_model=PaymentPreferenceResponse)
async def create_payment_preference(request: CreatePaymentRequest):
    """
    Crea una preferencia de pago en Mercado Pago.
    El cliente paga el total, ChangaRed recibe todo,
    y luego se transfiere el 80% al profesional.
    """
    if not sdk:
        raise HTTPException(
            status_code=503,
            detail="Mercado Pago no está configurado"
        )
    
    try:
        # Calcular montos
        monto_total = request.monto_total
        comision = monto_total * 0.20  # 20% para ChangaRed
        pago_profesional = monto_total * 0.80  # 80% para el profesional
        
        # Crear preferencia de pago
        preference_data = {
            "items": [
                {
                    "title": request.descripcion,
                    "quantity": 1,
                    "unit_price": float(monto_total),
                    "currency_id": "ARS"
                }
            ],
            "payer": {
                "name": request.cliente_nombre,
                "email": request.cliente_email
            },
            "back_urls": {
                "success": f"{os.environ['FRONTEND_URL']}/payment/success",
                "failure": f"{os.environ['FRONTEND_URL']}/payment/failure",
                "pending": f"{os.environ['FRONTEND_URL']}/payment/pending"
            },
            "auto_return": "approved",
            "external_reference": request.solicitud_id,
            "notification_url": f"{os.environ['BACKEND_URL']}/api/payments/webhook",
            "statement_descriptor": "CHANGARED",
            "metadata": {
                "solicitud_id": request.solicitud_id,
                "comision_changared": comision,
                "pago_profesional": pago_profesional
            }
        }
        
        # Crear preferencia
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        logger.info(f"Preferencia creada: {preference['id']} para solicitud {request.solicitud_id}")
        
        return PaymentPreferenceResponse(
            preference_id=preference["id"],
            init_point=preference["init_point"],
            sandbox_init_point=preference["sandbox_init_point"],
            monto_total=monto_total,
            comision_changared=comision,
            pago_profesional=pago_profesional
        )
        
    except Exception as e:
        logger.error(f"Error creando preferencia de pago: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear preferencia de pago: {str(e)}"
        )

@router.post("/webhook")
async def payment_webhook(notification_data: dict):
    """
    Webhook para recibir notificaciones de Mercado Pago
    cuando cambia el estado de un pago.
    """
    try:
        logger.info(f"Webhook recibido: {notification_data}")
        
        # Mercado Pago envía el tipo y el ID del pago
        if notification_data.get("type") == "payment":
            payment_id = notification_data.get("data", {}).get("id")
            
            if payment_id and sdk:
                # Obtener información del pago
                payment_info = sdk.payment().get(payment_id)
                payment = payment_info["response"]
                
                logger.info(f"Estado del pago {payment_id}: {payment.get('status')}")
                
                # Aquí podrías actualizar el estado en la base de datos
                # Por ejemplo, marcar la solicitud como "pagada"
                
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/status/{payment_id}")
async def get_payment_status(payment_id: str):
    """
    Obtiene el estado de un pago específico.
    """
    if not sdk:
        raise HTTPException(
            status_code=503,
            detail="Mercado Pago no está configurado"
        )
    
    try:
        payment_info = sdk.payment().get(payment_id)
        payment = payment_info["response"]
        
        return {
            "payment_id": payment_id,
            "status": payment.get("status"),
            "status_detail": payment.get("status_detail"),
            "transaction_amount": payment.get("transaction_amount"),
            "external_reference": payment.get("external_reference")
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del pago: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estado del pago: {str(e)}"
        )
