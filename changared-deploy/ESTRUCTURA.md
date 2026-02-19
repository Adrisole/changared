# 📁 Estructura de ChangaRed

```
changared/
├── backend/
│   ├── server.py                 # Servidor FastAPI principal
│   ├── mercadopago_routes.py     # Rutas de Mercado Pago
│   ├── requirements.txt          # Dependencias Python
│   └── .env.example             # Template de variables
│
├── frontend/
│   ├── public/                   # Archivos estáticos
│   ├── src/
│   │   ├── components/          # Componentes UI
│   │   │   ├── ui/             # Shadcn components
│   │   │   └── DashboardLayout.js
│   │   ├── contexts/
│   │   │   └── AuthContext.js   # Gestión de autenticación
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── AuthPage.js
│   │   │   ├── ClienteDashboard.js
│   │   │   └── AdminDashboard.js
│   │   ├── App.js               # App principal
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json             # Dependencias Node
│   ├── tailwind.config.js       # Config Tailwind
│   └── .env.example            # Template de variables
│
├── README.md                     # Documentación principal
├── DEPLOYMENT.md                 # Guía de deployment
├── design_guidelines.json        # Guía de diseño
└── .gitignore                   # Archivos a ignorar
```
