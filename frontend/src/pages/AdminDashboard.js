import React, { useState, useEffect } from 'react';
import { useAuth, API } from '../contexts/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { DollarSign, Users, FileText, TrendingUp, Zap, Droplets, Flame, Plus, Pencil, Trash2 } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function AdminDashboard() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [profesionales, setProfesionales] = useState([]);
  const [solicitudes, setSolicitudes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingProf, setEditingProf] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    telefono: '',
    email: '',
    tipo_servicio: 'electricista',
    latitud: -27.365,
    longitud: -55.896,
    disponible: true,
    tarifa_base: 15000
  });

  // Zonas predefinidas
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

  const handleZonaChange = (zona) => {
    const ubicacion = zonas[zona];
    setFormData({
      ...formData,
      latitud: ubicacion.lat,
      longitud: ubicacion.lon
    });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, profesionalesRes, solicitudesRes] = await Promise.all([
        axios.get(`${API}/admin/metrics`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/profesionales`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/solicitudes`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setMetrics(metricsRes.data);
      setProfesionales(profesionalesRes.data);
      setSolicitudes(solicitudesRes.data);
    } catch (error) {
      toast.error('Error al cargar datos');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingProf) {
        await axios.put(`${API}/profesionales/${editingProf.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Profesional actualizado');
      } else {
        await axios.post(`${API}/profesionales`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Profesional creado');
      }
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar profesional?')) return;
    try {
      await axios.delete(`${API}/profesionales/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Profesional eliminado');
      fetchData();
    } catch (error) {
      toast.error('Error al eliminar');
    }
  };

  const handleEdit = (prof) => {
    setEditingProf(prof);
    setFormData({
      nombre: prof.nombre,
      telefono: prof.telefono,
      email: prof.email,
      tipo_servicio: prof.tipo_servicio,
      latitud: prof.latitud,
      longitud: prof.longitud,
      disponible: prof.disponible,
      tarifa_base: prof.tarifa_base
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingProf(null);
    setFormData({
      nombre: '',
      telefono: '',
      email: '',
      tipo_servicio: 'electricista',
      latitud: -27.365,
      longitud: -55.896,
      disponible: true,
      tarifa_base: 5000
    });
  };

  const getServiceIcon = (tipo) => {
    const icons = {
      electricista: <Zap className="h-5 w-5" />,
      plomero: <Droplets className="h-5 w-5" />,
      gasista: <Flame className="h-5 w-5" />
    };
    return icons[tipo];
  };

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="admin-dashboard">
        <div>
          <h1 className="text-3xl font-heading font-bold" data-testid="admin-title">Panel de Administración</h1>
          <p className="text-slate-600">Gestión completa de ChangaRed</p>
        </div>

        {/* Metrics */}
        {metrics && (
          <div className="grid md:grid-cols-4 gap-6" data-testid="metrics-section">
            <Card className="border-l-4 border-l-primary">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Total Solicitudes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-3xl font-bold" data-testid="total-solicitudes">{metrics.total_solicitudes}</div>
                  <FileText className="h-8 w-8 text-primary" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Completadas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-3xl font-bold" data-testid="solicitudes-completadas">{metrics.solicitudes_completadas}</div>
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Comisiones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-3xl font-bold" data-testid="total-comisiones">${metrics.total_comisiones.toFixed(2)}</div>
                  <DollarSign className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Profesionales</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-3xl font-bold" data-testid="profesionales-activos">{metrics.profesionales_activos}</div>
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Profesionales */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-heading font-bold">Gestión de Profesionales</h2>
            <Button onClick={() => setShowForm(!showForm)} data-testid="agregar-profesional-button">
              <Plus className="h-4 w-4 mr-2" />
              {showForm ? 'Cancelar' : 'Agregar Profesional'}
            </Button>
          </div>

          {showForm && (
            <Card className="mb-6" data-testid="profesional-form">
              <CardContent className="p-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Nombre</Label>
                      <Input value={formData.nombre} onChange={(e) => setFormData({ ...formData, nombre: e.target.value })} required data-testid="prof-nombre-input" />
                    </div>
                    <div className="space-y-2">
                      <Label>Teléfono</Label>
                      <Input value={formData.telefono} onChange={(e) => setFormData({ ...formData, telefono: e.target.value })} required data-testid="prof-telefono-input" />
                    </div>
                    <div className="space-y-2">
                      <Label>Email</Label>
                      <Input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required data-testid="prof-email-input" />
                    </div>
                    <div className="space-y-2">
                      <Label>Tipo de Servicio</Label>
                      <select value={formData.tipo_servicio} onChange={(e) => setFormData({ ...formData, tipo_servicio: e.target.value })} className="w-full h-12 rounded-lg border border-slate-200 px-3 bg-slate-50" data-testid="prof-tipo-select">
                        <option value="electricista">Electricista</option>
                        <option value="plomero">Plomero</option>
                        <option value="gasista">Gasista</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Zona de Trabajo</Label>
                      <select 
                        onChange={(e) => handleZonaChange(e.target.value)} 
                        className="w-full h-12 rounded-lg border border-slate-200 px-3 bg-slate-50"
                      >
                        <option value="">Seleccionar zona...</option>
                        {Object.entries(zonas).map(([key, zona]) => (
                          <option key={key} value={key}>
                            {zona.nombre}
                          </option>
                        ))}
                      </select>
                      <p className="text-xs text-slate-500">
                        O ingresa coordenadas manualmente abajo
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Latitud</Label>
                      <Input type="number" step="any" value={formData.latitud} onChange={(e) => setFormData({ ...formData, latitud: parseFloat(e.target.value) })} required data-testid="prof-latitud-input" />
                    </div>
                    <div className="space-y-2">
                      <Label>Longitud</Label>
                      <Input type="number" step="any" value={formData.longitud} onChange={(e) => setFormData({ ...formData, longitud: parseFloat(e.target.value) })} required data-testid="prof-longitud-input" />
                    </div>
                    <div className="space-y-2">
                      <Label>Tarifa Base (ARS)</Label>
                      <Input type="number" step="100" value={formData.tarifa_base} onChange={(e) => setFormData({ ...formData, tarifa_base: parseFloat(e.target.value) })} required data-testid="prof-tarifa-input" />
                      <p className="text-xs text-slate-500">
                        Recomendado: $15,000 - $20,000 por servicio
                      </p>
                    </div>
                    <div className="space-y-2 flex items-center">
                      <input type="checkbox" checked={formData.disponible} onChange={(e) => setFormData({ ...formData, disponible: e.target.checked })} className="mr-2" data-testid="prof-disponible-checkbox" />
                      <Label>Disponible</Label>
                    </div>
                  </div>
                  <Button type="submit" data-testid="submit-profesional-button">{editingProf ? 'Actualizar' : 'Crear'} Profesional</Button>
                </form>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4">
            {profesionales.map((prof) => (
              <Card key={prof.id} data-testid={`prof-card-${prof.id}`}>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex gap-4 flex-1">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-primary">
                        {getServiceIcon(prof.tipo_servicio)}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-heading font-bold text-lg">{prof.nombre}</h3>
                        <p className="text-sm text-slate-600">{prof.email} | {prof.telefono}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge className="capitalize">{prof.tipo_servicio}</Badge>
                          <Badge variant={prof.disponible ? 'secondary' : 'destructive'}>
                            {prof.disponible ? 'Disponible' : 'No disponible'}
                          </Badge>
                        </div>
                        <div className="mt-2 text-sm text-slate-600">
                          <span className="font-semibold">Tarifa:</span> ${prof.tarifa_base} | 
                          <span className="font-semibold ml-2">Servicios:</span> {prof.total_servicios} | 
                          <span className="font-semibold ml-2">Ganado:</span> ${prof.total_ganado.toFixed(2)}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => handleEdit(prof)} data-testid="edit-prof-button">
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDelete(prof.id)} data-testid="delete-prof-button">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Solicitudes */}
        <div>
          <h2 className="text-2xl font-heading font-bold mb-4">Todas las Solicitudes</h2>
          <div className="grid gap-4">
            {solicitudes.slice(0, 10).map((sol) => (
              <Card key={sol.id} data-testid={`solicitud-card-${sol.id}`}>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-heading font-bold capitalize">{sol.servicio}</h3>
                        <Badge variant={sol.urgencia === 'urgente' ? 'destructive' : 'secondary'}>{sol.urgencia}</Badge>
                        <Badge variant="outline">{sol.estado}</Badge>
                      </div>
                      <p className="text-sm text-slate-600 mb-2">
                        <span className="font-semibold">Cliente:</span> {sol.cliente_nombre} | 
                        <span className="font-semibold ml-2">Profesional:</span> {sol.profesional_nombre}
                      </p>
                      <p className="text-sm text-slate-700">{sol.mensaje_cliente}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary">${sol.precio_total.toFixed(2)}</div>
                      <div className="text-xs text-slate-600">Comisión: ${sol.comision_changared.toFixed(2)}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}