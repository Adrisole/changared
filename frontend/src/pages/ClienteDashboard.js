import React, { useState, useEffect } from 'react';
import { useAuth, API } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { MapPin, Clock, DollarSign, User, Zap, Droplets, Flame, Loader2 } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function ClienteDashboard() {
  const { user, token } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [ubicacionMode, setUbicacionMode] = useState('zona'); // 'zona' o 'auto'
  const [formData, setFormData] = useState({
    mensaje_cliente: '',
    latitud: -27.365,
    longitud: -55.896,
    urgencia: 'normal',
    zona: 'centro'
  });

  // Zonas predefinidas de Posadas, Misiones
  const zonas = {
    centro: { lat: -27.3671, lon: -55.8961, nombre: 'Centro' },
    villa_sarita: { lat: -27.3848, lon: -55.8866, nombre: 'Villa Sarita' },
    san_lorenzo: { lat: -27.3533, lon: -55.9180, nombre: 'San Lorenzo' },
    miguel_lanús: { lat: -27.3927, lon: -55.9145, nombre: 'Miguel Lanús' },
    villa_cabello: { lat: -27.3438, lon: -55.8742, nombre: 'Villa Cabello' },
    itaembé_miní: { lat: -27.4172, lon: -55.9319, nombre: 'Itaembé Miní' },
    villa_urquiza: { lat: -27.3281, lon: -55.9087, nombre: 'Villa Urquiza' },
    el_brete: { lat: -27.4384, lon: -55.9548, nombre: 'El Brete' }
  };

  useEffect(() => {
    fetchSolicitudes();
  }, []);

  const obtenerUbicacionAutomatica = () => {
    if (navigator.geolocation) {
      setLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData({
            ...formData,
            latitud: position.coords.latitude,
            longitud: position.coords.longitude
          });
          setLoading(false);
          toast.success('Ubicación obtenida correctamente');
        },
        (error) => {
          setLoading(false);
          toast.error('No se pudo obtener tu ubicación. Selecciona una zona.');
          console.error('Error de geolocalización:', error);
        }
      );
    } else {
      toast.error('Tu navegador no soporta geolocalización. Selecciona una zona.');
    }
  };

  const handleZonaChange = (zona) => {
    const ubicacion = zonas[zona];
    setFormData({
      ...formData,
      zona: zona,
      latitud: ubicacion.lat,
      longitud: ubicacion.lon
    });
  };

  const fetchSolicitudes = async () => {
    try {
      const response = await axios.get(`${API}/solicitudes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSolicitudes(response.data);
    } catch (error) {
      console.error('Error fetching solicitudes:', error);
      toast.error('Error al cargar solicitudes');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/solicitudes`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('¡Solicitud creada! Profesional asignado.');
      setFormData({ mensaje_cliente: '', latitud: -27.365, longitud: -55.896, urgencia: 'normal' });
      setShowForm(false);
      fetchSolicitudes();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear solicitud');
    } finally {
      setLoading(false);
    }
  };

  const handlePagar = async (solicitud) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/payments/create-preference`, {
        solicitud_id: solicitud.id,
        cliente_email: user.email,
        cliente_nombre: user.nombre,
        monto_total: solicitud.precio_total,
        descripcion: `${solicitud.servicio} - ${solicitud.mensaje_cliente}`
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Redirigir a Mercado Pago
      window.location.href = response.data.init_point;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear pago');
    } finally {
      setLoading(false);
    }
  };

  const getServiceIcon = (servicio) => {
    const icons = {
      electricista: <Zap className="h-5 w-5" />,
      plomero: <Droplets className="h-5 w-5" />,
      gasista: <Flame className="h-5 w-5" />
    };
    return icons[servicio] || <User className="h-5 w-5" />;
  };

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="cliente-dashboard">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-heading font-bold" data-testid="dashboard-title">Bienvenido, {user?.nombre}</h1>
            <p className="text-slate-600">Solicita servicios profesionales en segundos</p>
          </div>
          <Button 
            onClick={() => setShowForm(!showForm)} 
            size="lg"
            data-testid="nueva-solicitud-button"
          >
            {showForm ? 'Cancelar' : 'Nueva Solicitud'}
          </Button>
        </div>

        {showForm && (
          <Card data-testid="nueva-solicitud-form">
            <CardHeader>
              <CardTitle>Nueva Solicitud de Servicio</CardTitle>
              <CardDescription>Describe tu problema y te asignaremos el profesional adecuado</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="mensaje">Describe tu problema</Label>
                  <Textarea
                    id="mensaje"
                    placeholder="Ej: Se me cortó la luz en toda la casa y necesito un electricista urgente"
                    value={formData.mensaje_cliente}
                    onChange={(e) => setFormData({ ...formData, mensaje_cliente: e.target.value })}
                    rows={4}
                    required
                    data-testid="mensaje-textarea"
                  />
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="latitud">Latitud</Label>
                    <Input
                      id="latitud"
                      type="number"
                      step="any"
                      value={formData.latitud}
                      onChange={(e) => setFormData({ ...formData, latitud: parseFloat(e.target.value) })}
                      required
                      data-testid="latitud-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="longitud">Longitud</Label>
                    <Input
                      id="longitud"
                      type="number"
                      step="any"
                      value={formData.longitud}
                      onChange={(e) => setFormData({ ...formData, longitud: parseFloat(e.target.value) })}
                      required
                      data-testid="longitud-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="urgencia">Urgencia</Label>
                    <select
                      id="urgencia"
                      value={formData.urgencia}
                      onChange={(e) => setFormData({ ...formData, urgencia: e.target.value })}
                      className="w-full h-12 rounded-lg border border-slate-200 px-3 bg-slate-50"
                      data-testid="urgencia-select"
                    >
                      <option value="normal">Normal</option>
                      <option value="urgente">Urgente (+30%)</option>
                    </select>
                  </div>
                </div>
                <Button type="submit" disabled={loading} className="w-full" data-testid="submit-solicitud-button">
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Solicitar Servicio
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        <div>
          <h2 className="text-2xl font-heading font-bold mb-4">Mis Solicitudes</h2>
          {solicitudes.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <p className="text-slate-500">No tienes solicitudes aún. ¡Crea tu primera solicitud!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {solicitudes.map((solicitud) => (
                <Card key={solicitud.id} className="hover:shadow-lg transition-shadow" data-testid={`solicitud-card-${solicitud.id}`}>
                  <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row justify-between gap-4">
                      <div className="flex-1 space-y-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-primary">
                            {getServiceIcon(solicitud.servicio)}
                          </div>
                          <div>
                            <h3 className="font-heading font-bold text-lg capitalize">{solicitud.servicio}</h3>
                            <p className="text-sm text-slate-600">{new Date(solicitud.created_at).toLocaleString('es-AR')}</p>
                          </div>
                        </div>
                        <p className="text-slate-700">{solicitud.mensaje_cliente}</p>
                        <div className="flex flex-wrap gap-2">
                          <Badge variant={solicitud.urgencia === 'urgente' ? 'destructive' : 'secondary'} data-testid="urgencia-badge">
                            {solicitud.urgencia === 'urgente' ? <Clock className="h-3 w-3 mr-1" /> : null}
                            {solicitud.urgencia}
                          </Badge>
                          <Badge variant="outline" data-testid="estado-badge">{solicitud.estado}</Badge>
                        </div>
                      </div>
                      <div className="border-l pl-6 space-y-2 min-w-[200px]">
                        <div className="flex items-center gap-2 text-sm">
                          <User className="h-4 w-4 text-slate-400" />
                          <span className="font-semibold">{solicitud.profesional_nombre}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <MapPin className="h-4 w-4 text-slate-400" />
                          <span>{solicitud.distancia_km} km</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <DollarSign className="h-5 w-5 text-primary" />
                          <span className="text-2xl font-bold text-primary">${solicitud.precio_total.toFixed(2)}</span>
                        </div>
                        {solicitud.estado_pago === 'sin_pagar' && (
                          <Button
                            size="sm"
                            onClick={() => handlePagar(solicitud)}
                            className="w-full mt-2"
                            data-testid="pagar-button"
                          >
                            Pagar Ahora
                          </Button>
                        )}
                        {solicitud.estado_pago === 'pagado' && (
                          <Badge variant="secondary" className="w-full justify-center">
                            ✓ Pagado
                          </Badge>
                        )}
                      </div>
                    </div>
                    {solicitud.mensaje_respuesta && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg border-l-4 border-primary">
                        <p className="text-sm font-semibold text-blue-900 mb-1">Respuesta:</p>
                        <p className="text-sm text-blue-800">{solicitud.mensaje_respuesta}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}