# ChangaRed - Product Requirements Document
**Última actualización: Febrero 2026**

## Descripción del Proyecto
ChangaRed es una plataforma que conecta clientes con profesionales de servicios (electricistas, plomeros, gasistas, etc.) en Misiones, Argentina. El admin (dueña) opera como intermediaria entre clientes y profesionales.

## Arquitectura Actual
- **Backend**: FastAPI (Python) — `backend/server.py`
- **Frontend**: React.js + Tailwind CSS
- **Base de datos**: MongoDB Atlas (cloud)
- **IA**: GPT-4o-mini via Emergent LLM
- **Pagos**: Mercado Pago API
- **Notificaciones**: Telegram Bot + Email (Gmail SMTP)
- **Deploy frontend**: Vercel
- **Deploy backend**: Vercel (mismo proyecto)
- **Dominio**: changared.com (conectado via Namecheap)

## Flujo de Negocio Real

### Paso a paso:
1. **Cliente** describe su problema en la app y marca si es urgente
2. **IA** detecta el tipo de servicio y calcula rango de precio
3. Si es urgente → precio +30% automático
4. **Admin recibe Telegram** con todos los datos para reenviar a grupos de WhatsApp
5. Admin envía a grupos de WhatsApp de profesionales
6. El profesional que acepta avisa por WhatsApp
7. Admin asigna desde el dashboard
8. **Profesional recibe email** con detalles del trabajo y su pago
9. **Cliente paga** via Mercado Pago
10. Admin le transfiere el 90% al profesional cuando quiera (diario/semanal)

### Comisión:
- Cliente ve el precio final (ej: $20.000)
- Profesional recibe 90% ($18.000)
- ChangaRed retiene 10% ($2.000)
- La comisión NO se suma al precio — sale de él

### Mensaje de Telegram al admin:
```
NUEVA SOLICITUD - ChangaRed
Servicio: ELECTRICISTA
Problema: Se me fue la luz
Zona: Posadas

Cliente: Juan Pérez
Tel: 3764-123456

Precio acordado: $18.000 - $22.500

ID: abc123
```

## Roles de Usuario
- **Cliente**: Solicita servicios, ve cotizaciones, paga via Mercado Pago
- **Profesional**: Se registra con su oficio y zona, recibe emails de trabajos asignados
- **Admin**: Recibe Telegram, asigna profesionales, gestiona pagos (acceso directo a MongoDB o dashboard)

> Nota: El rol admin NO está disponible en el registro público por seguridad.
> Para crear admin: insertar directamente en MongoDB con `"rol": "admin"`.

## Servicios Disponibles (15)
1. electricista
2. plomero
3. gasista
4. pintor
5. carpintero
6. limpieza
7. jardinero
8. cerrajero
9. técnico aire acondicionado
10. técnico lavarropas
11. técnico heladeras
12. técnico electrodomésticos
13. albañil
14. mudanza
15. técnico general

## Zonas Cubiertas (20)
Posadas, Garupá, Candelaria, Santa Ana, San Ignacio, Jardín América, Oberá, Apóstoles, Azara, San José, Eldorado, Puerto Iguazú, Wanda, Montecarlo, Puerto Rico, Leandro N. Alem, Campo Grande, Aristóbulo del Valle, San Vicente, Bernardo de Irigoyen

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/register | Registro de usuario |
| POST | /api/login | Login |
| GET | /api/me | Usuario actual |
| POST | /api/solicitudes | Crear solicitud (cliente) |
| GET | /api/solicitudes | Listar solicitudes |
| PUT | /api/solicitudes/{id} | Actualizar solicitud |
| PUT | /api/admin/solicitudes/{id}/accion | Admin acepta/rechaza |
| POST | /api/solicitudes/{id}/pago | Generar link MP |
| GET | /api/profesionales | Listar profesionales |
| PUT | /api/profesionales/disponibilidad | Toggle disponibilidad |
| GET | /api/health | Health check |

## Variables de Entorno (Vercel)
```
MONGO_URL
SECRET_KEY
EMERGENT_API_KEY
MERCADOPAGO_ACCESS_TOKEN
MERCADOPAGO_PUBLIC_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_ADMIN_CHAT_ID
SMTP_USER
SMTP_PASS
CI = false
```

## Archivos Clave
```
backend/server.py                          — Lógica principal, IA, endpoints
frontend/src/contexts/AuthContext.js       — Login, registro, token JWT
frontend/src/pages/AuthPage.js             — Formulario registro/login
frontend/src/pages/AdminDashboard.js       — Panel de admin
frontend/src/pages/ProfesionalDashboard.js — Panel de profesional
frontend/src/pages/ClienteDashboard.js     — Panel de cliente
```

## Bugs Resueltos
1. ~~IA clasificaba "limpieza de alfombra" como "gasista"~~ — Corregido con fallback por palabras clave
2. ~~Admin disponible en registro público~~ — Eliminado por seguridad
3. ~~Profesional se registraba sin seleccionar oficio~~ — Agregado selector de servicio y zona
4. ~~Endpoints del frontend no coincidían con backend~~ — Corregido en AuthContext.js (`/api/me` sin `/auth/`)
5. ~~Comisión se sumaba al precio del cliente~~ — Corregido: sale del precio, no se suma
6. ~~Funciones de Telegram/Email definidas después de usarse~~ — Movidas al inicio del archivo
7. ~~Logo deformado en landing page~~ — Corregido con object-contain

## Backlog Priorizado

### P1 — Alta prioridad
- [ ] Probar flujo completo: registro → solicitud → Telegram → asignación → pago
- [ ] Crear usuario admin directo en MongoDB
- [ ] Verificar que email a profesionales funciona (requiere SMTP_PASS de Gmail)

### P2 — Media prioridad
- [ ] Botón "Trabajo completado" en dashboard profesional
- [ ] Dashboard admin con lista de solicitudes pendientes y botón asignar
- [ ] Tabla de precios pública en la landing page

### P3 — Baja prioridad
- [ ] Chat cliente-profesional dentro de la app
- [ ] Calificaciones post-trabajo
- [ ] Modelo de subasta (múltiples profesionales ofertan)

## Modelo de Monetización
- **Freemium para profesionales**: 3 trabajos gratis, luego elegir entre:
  - 10% de comisión por trabajo (ya implementado)
  - Suscripción mensual fija (pendiente implementar)
- **Publicidad**: $11.305 USD en Facebook Ads ya asignados para adquisición de clientes
- **40 profesionales** ya reclutados al momento de este documento
