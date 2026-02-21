import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

const TIPOS_SERVICIO = [
  { value: 'electricista', label: 'Electricista' },
  { value: 'plomero', label: 'Plomero' },
  { value: 'gasista', label: 'Gasista' },
  { value: 'tecnico_lavarropas', label: 'Técnico en Lavarropas' },
  { value: 'tecnico_tv', label: 'Técnico en TV' },
  { value: 'tecnico_heladeras', label: 'Técnico en Heladeras' },
  { value: 'tecnico_aire', label: 'Técnico en Aire Acondicionado' },
  { value: 'limpieza', label: 'Limpieza' },
  { value: 'fletes', label: 'Fletes y Mudanzas' },
  { value: 'albanil', label: 'Albañil' },
  { value: 'jardinero_poda', label: 'Jardinero / Poda' },
  { value: 'pintor', label: 'Pintor' },
  { value: 'ninero_cuidador', label: 'Niñero / Cuidador' },
  { value: 'tapiceria', label: 'Tapicería' },
  { value: 'herreria', label: 'Herrería' }
];

const ZONAS = [
  'Posadas',
  'Garupá',
  'Candelaria',
  'Santa Ana',
  'Corpus',
  'San Ignacio',
  'Jardín América',
  'Oberá',
  'Apóstoles',
  'Azara',
  'San José',
  'Eldorado',
  'Puerto Iguazú',
  'Wanda',
  'Montecarlo',
  'Puerto Rico',
  'Leandro N. Alem',
  'Campo Grande',
  'Aristóbulo del Valle',
  'San Vicente',
  'Bernardo de Irigoyen',
];

export default function AuthPage() {
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    nombre: '',
    telefono: '',
    rol: 'cliente',
    tipo_servicio: 'electricista',
    zona: 'Posadas'
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(loginData.email, loginData.password);
      toast.success('¡Bienvenido a ChangaRed!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(registerData);
      toast.success('¡Cuenta creada exitosamente!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al registrarse');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 p-6">
      <Card className="w-full max-w-md" data-testid="auth-card">
        <CardHeader className="space-y-2 text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_1ccdb137-8865-4cb4-b134-9dea2c01f7a6/artifacts/klhc20tm_ChangaRed_Logo_IG_320x320%20-%20Editado.png" 
            alt="ChangaRed Logo" 
            className="h-20 mx-auto mb-4 object-contain"
            data-testid="logo-image"
          />
          <CardTitle className="text-2xl font-heading font-bold">Bienvenido a ChangaRed</CardTitle>
          <CardDescription>Conectamos profesionales con clientes</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login" data-testid="login-tab">Iniciar Sesión</TabsTrigger>
              <TabsTrigger value="register" data-testid="register-tab">Registrarse</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4" data-testid="login-form">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="tu@email.com"
                    value={loginData.email}
                    onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                    required
                    data-testid="login-email-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="login-password">Contraseña</Label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="••••••••"
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    required
                    data-testid="login-password-input"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={loading}
                  data-testid="login-submit-button"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Iniciar Sesión
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-4" data-testid="register-form">
                <div className="space-y-2">
                  <Label htmlFor="register-nombre">Nombre Completo</Label>
                  <Input
                    id="register-nombre"
                    placeholder="Juan Pérez"
                    value={registerData.nombre}
                    onChange={(e) => setRegisterData({ ...registerData, nombre: e.target.value })}
                    required
                    data-testid="register-nombre-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="register-telefono">Teléfono</Label>
                  <Input
                    id="register-telefono"
                    placeholder="+54 376 123-4567"
                    value={registerData.telefono}
                    onChange={(e) => setRegisterData({ ...registerData, telefono: e.target.value })}
                    required
                    data-testid="register-telefono-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="register-email">Email</Label>
                  <Input
                    id="register-email"
                    type="email"
                    placeholder="tu@email.com"
                    value={registerData.email}
                    onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                    required
                    data-testid="register-email-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="register-password">Contraseña</Label>
                  <Input
                    id="register-password"
                    type="password"
                    placeholder="••••••••"
                    value={registerData.password}
                    onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                    required
                    data-testid="register-password-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="register-rol">Tipo de Cuenta</Label>
                  <select
                    id="register-rol"
                    value={registerData.rol}
                    onChange={(e) => setRegisterData({ ...registerData, rol: e.target.value })}
                    className="w-full h-12 rounded-lg border border-slate-200 px-3 bg-slate-50"
                    data-testid="register-rol-select"
                  >
                    <option value="cliente">Cliente</option>
                    <option value="profesional">Profesional / Changarin</option>
                  </select>
                </div>

                {registerData.rol === 'profesional' && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="register-servicio">¿Qué servicio ofrecés?</Label>
                      <select
                        id="register-servicio"
                        value={registerData.tipo_servicio}
                        onChange={(e) => setRegisterData({ ...registerData, tipo_servicio: e.target.value })}
                        className="w-full h-12 rounded-lg border border-slate-200 px-3 bg-slate-50"
                        data-testid="register-servicio-select"
                        required
                      >
                        {TIPOS_SERVICIO.map(tipo => (
                          <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="register-zona">Zona de trabajo</Label>
                      <select
                        id="register-zona"
                        value={registerData.zona}
                        onChange={(e) => setRegisterData({ ...registerData, zona: e.target.value })}
                        className="w-full h-12 rounded-lg border border-slate-200 px-3 bg-slate-50"
                        data-testid="register-zona-select"
                      >
                        {ZONAS.map(zona => (
                          <option key={zona} value={zona}>{zona}</option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={loading}
                  data-testid="register-submit-button"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Crear Cuenta
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
