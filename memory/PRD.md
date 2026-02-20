# ChangaRed - Product Requirements Document

## Original Problem Statement
ChangaRed es una aplicación que conecta profesionales de servicios (electricistas, plomeros, gasistas, etc.) con clientes en Posadas, Argentina. La aplicación:
1. Recibe solicitudes de servicio de clientes en tiempo real
2. Usa IA para determinar automáticamente el tipo de servicio
3. Calcula precios basados en tablas específicas para Posadas
4. Asigna profesionales cercanos
5. Integra con Mercado Pago para pagos
6. Notifica al admin vía Telegram

## User Personas
- **Cliente**: Solicita servicios, ve cotizaciones, paga vía Mercado Pago
- **Profesional**: Recibe y acepta/rechaza trabajos asignados
- **Admin**: Recibe notificaciones, asigna profesionales manualmente

## Core Requirements
- 15+ categorías de servicios con precios específicos
- Sistema de autenticación (cliente, profesional, admin)
- Flujo híbrido de asignación (admin manual con sugerencias de IA)
- Integración con Mercado Pago
- Notificaciones por Telegram al admin

## Current Architecture
- **Backend**: FastAPI (Python) - `/app/backend/server.py`
- **Frontend**: React.js + Tailwind CSS
- **Database**: MongoDB
- **AI**: OpenAI GPT-4o-mini via Emergent Integration
- **Payments**: Mercado Pago API
- **Notifications**: Telegram Bot API

## What's Been Implemented
### February 20, 2026
- [x] Full-stack application (React + FastAPI + MongoDB)
- [x] User authentication (cliente, profesional, admin roles)
- [x] AI-powered service classification with 15+ categories
- [x] Price calculation based on user-provided tables
- [x] Mercado Pago integration
- [x] Telegram notifications to admin
- [x] Hybrid assignment workflow (admin receives suggestions, assigns manually)
- [x] Professional accept/reject workflow
- [x] **FIX: AI service misclassification bug** - "limpieza de alfombra" now correctly classified as "limpieza"
- [x] **FIX: Added fallback keyword detection** for when AI returns malformed JSON
- [x] **FIX: Logo visibility** - Added white background to logo in hero section
- [x] GitHub repository setup and code push

## Prioritized Backlog

### P1 - High Priority
- [ ] **Estado "Completado" para trabajos** - Botón para que profesionales marquen trabajos como finalizados
- [ ] **Notificaciones automáticas a profesionales** - Email cuando se les asigna un trabajo

### P2 - Medium Priority  
- [ ] **Tabla de precios pública** - Página pública con rangos de precio por servicio
- [ ] **Chat cliente-profesional** - Comunicación in-app después de confirmar trabajo

### P3 - Low Priority
- [ ] **Modelo de subastas** - Múltiples profesionales ofertan, cliente elige

## Key Files
- `/app/backend/server.py` - Core backend logic, AI prompts, CRUD
- `/app/frontend/src/pages/AdminDashboard.js` - Admin UI
- `/app/frontend/src/pages/ProfesionalDashboard.js` - Professional UI
- `/app/frontend/src/pages/ClienteDashboard.js` - Client UI
- `/app/backend/.env` - API keys (Mercado Pago, Telegram)

## Known Issues Resolved
1. ~~AI misclassifying "limpieza de alfombra" as "gasista"~~ - Fixed with improved prompt and fallback detection
2. ~~Logo deformation on landing page~~ - Fixed with object-contain and white background

## 3rd Party Integrations
- **OpenAI GPT-4o-mini**: Service classification (uses Emergent LLM Key)
- **Mercado Pago**: Payment processing (user API keys configured)
- **Telegram**: Admin notifications (user bot token configured)

## Testing Status
- Backend API endpoints: Tested via curl
- AI classification: Tested with multiple service types
- Authentication flow: Tested login/register
- Frontend screens: Verified via screenshots
