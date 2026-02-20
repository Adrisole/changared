import React, { useState, useEffect } from 'react';
import { useAuth, API } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { MapPin, Clock, DollarSign, CheckCircle, XCircle, AlertCircle, Phone, User as UserIcon } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

export default function ProfesionalDashboard() {
  const { user, token } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    pendientes: 0,
    confirmadas: 0,
    completadas: 0,
    total_ganado: 0
  });

  useEffect(() => {
    fetchSolicitudes();
  }, []);

  const fetchSolicitudes = async () => {
    try {
      const response = await axios.get(`${API}/solicitudes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSolicitudes(response.data);
      
      // Calcular stats
      const pendientes = response.data.filter(s => s.estado === 'pendiente_confirmacion').length;
      const confirmadas = response.data.filter(s => s.estado === 'confirmado').length;
      const completadas = response.data.filter(s => s.estado === 'completado').length;
      const total_ganado = response.data
        .filter(s => s.estado === 'completado')
        .reduce((sum, s) => sum + s.pago_profesional, 0);
      
      setStats({ pendientes, confirmadas, completadas, total_ganado });
    } catch (error) {
      console.error('Error fetching solicitudes:', error);
      toast.error('Error al cargar solicitudes');
    }
  };

  const handleAceptar = async (solicitudId) => {
    setLoading(true);
    try {
      await axios.post(`${API}/solicitudes/${solicitudId}/aceptar`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('¡Solicitud aceptada! El cliente recibirá tu confirmación.');
      fetchSolicitudes();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al aceptar');
    } finally {
      setLoading(false);
    }
  };

  const handleRechazar = async (solicitudId) => {
    if (!window.confirm('¿Seguro que quieres rechazar esta solicitud? Se asignará a otro profesional.')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/solicitudes/${solicitudId}/rechazar`, 
        { motivo: 'No disponible' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.reasignado) {
        toast.success(`Solicitud reasignada a ${response.data.nuevo_profesional}`);
      } else {
        toast.info('Solicitud rechazada. No hay más profesionales disponibles.');
      }
      fetchSolicitudes();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al rechazar');
    } finally {
      setLoading(false);
    }
  };

  const getEstadoBadge = (estado) => {
    const badges = {
      pendiente_confirmacion: <Badge variant="default" className="bg-amber-500"><AlertCircle className="h-3 w-3 mr-1" /> Pendiente Confirmar</Badge>,
      confirmado: <Badge variant="secondary" className="bg-blue-500 text-white"><CheckCircle className="h-3 w-3 mr-1" /> Confirmado</Badge>,
      en_proceso: <Badge variant="secondary" className="bg-purple-500 text-white"><Clock className="h-3 w-3 mr-1" /> En Proceso</Badge>,
      completado: <Badge variant="secondary" className="bg-green-600 text-white"><CheckCircle className="h-3 w-3 mr-1" /> Completado</Badge>,
      cancelado: <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" /> Cancelado</Badge>
    };
    return badges[estado] || <Badge>{estado}</Badge>;
  };

  const pendientes = solicitudes.filter(s => s.estado === 'pendiente_confirmacion');
  const confirmadas = solicitudes.filter(s => s.estado === 'confirmado' || s.estado === 'en_proceso');
  const historial = solicitudes.filter(s => s.estado === 'completado' || s.estado === 'cancelado');

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="profesional-dashboard">
        <div>
          <h1 className="text-3xl font-heading font-bold" data-testid="dashboard-title">Hola, {user?.nombre}</h1>
          <p className="text-slate-600">Panel de Profesional - Gestiona tus solicitudes</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-amber-500">
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-amber-600" data-testid="pendientes-count">{stats.pendientes}</div>
              <p className="text-sm text-slate-600">Pendientes Confirmar</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-blue-600" data-testid="confirmadas-count">{stats.confirmadas}</div>
              <p className="text-sm text-slate-600">Confirmadas</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-green-500">
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-green-600" data-testid="completadas-count">{stats.completadas}</div>
              <p className="text-sm text-slate-600">Completadas</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-primary">
            <CardContent className="p-6">
              <div className="text-2xl font-bold text-primary" data-testid="total-ganado">${stats.total_ganado.toLocaleString()}</div>
              <p className="text-sm text-slate-600">Total Ganado</p>
            </CardContent>
          </Card>
        </div>

        {/* Solicitudes Pendientes */}
        {pendientes.length > 0 && (
          <div>
            <h2 className="text-2xl font-heading font-bold mb-4 text-amber-600">
              ⚠️ Solicitudes Pendientes de Confirmar ({pendientes.length})
            </h2>
            <div className="grid gap-4">
              {pendientes.map((solicitud) => (
                <Card key={solicitud.id} className="border-2 border-amber-500 shadow-lg" data-testid={`solicitud-pendiente-${solicitud.id}`}>
                  <CardHeader className="bg-amber-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="capitalize">{solicitud.servicio.replace('_', ' ')} - {solicitud.categoria_trabajo.replace('_', ' ')}</CardTitle>
                        <CardDescription>{new Date(solicitud.created_at).toLocaleString('es-AR')}</CardDescription>
                      </div>
                      {getEstadoBadge(solicitud.estado)}
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Descripción del cliente:</p>
                        <p className="text-slate-700">{solicitud.mensaje_cliente}</p>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm">
                            <UserIcon className="h-4 w-4 text-slate-400" />
                            <span className="font-semibold">Cliente:</span> {solicitud.cliente_nombre}
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <MapPin className="h-4 w-4 text-slate-400" />
                            <span className="font-semibold">Distancia:</span> {solicitud.distancia_km} km
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Clock className="h-4 w-4 text-slate-400" />
                            <Badge variant={solicitud.urgencia === 'urgente' ? 'destructive' : 'secondary'}>
                              {solicitud.urgencia}
                            </Badge>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                            <p className="text-sm text-slate-600 mb-1">Tu pago será:</p>
                            <div className="flex items-center gap-2">
                              <DollarSign className="h-6 w-6 text-green-600" />
                              <span className="text-3xl font-bold text-green-600" data-testid="pago-profesional">
                                ${solicitud.pago_profesional.toLocaleString()}
                              </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-1">Cliente paga: ${solicitud.precio_total.toLocaleString()}</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-3">
                        <Button 
                          onClick={() => handleAceptar(solicitud.id)}
                          disabled={loading}
                          className="flex-1 bg-green-600 hover:bg-green-700"
                          data-testid="aceptar-button"
                        >
                          <CheckCircle className="h-5 w-5 mr-2" />
                          ACEPTAR SOLICITUD
                        </Button>
                        <Button 
                          onClick={() => handleRechazar(solicitud.id)}
                          disabled={loading}
                          variant="outline"
                          className="flex-1"
                          data-testid="rechazar-button"
                        >
                          <XCircle className="h-5 w-5 mr-2" />
                          RECHAZAR
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Solicitudes Confirmadas */}
        {confirmadas.length > 0 && (
          <div>
            <h2 className="text-2xl font-heading font-bold mb-4">Trabajos Confirmados ({confirmadas.length})</h2>
            <div className="grid gap-4">
              {confirmadas.map((solicitud) => (
                <Card key={solicitud.id} data-testid={`solicitud-confirmada-${solicitud.id}`}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-heading font-bold text-lg capitalize">{solicitud.servicio.replace('_', ' ')}</h3>
                        <p className="text-sm text-slate-600">{solicitud.mensaje_cliente}</p>
                      </div>
                      {getEstadoBadge(solicitud.estado)}
                    </div>
                    <div className="grid md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-semibold">Cliente:</span> {solicitud.cliente_nombre}
                      </div>
                      <div>
                        <span className="font-semibold">Distancia:</span> {solicitud.distancia_km} km
                      </div>
                      <div>
                        <span className="font-semibold">Tu pago:</span> ${solicitud.pago_profesional.toLocaleString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Historial */}
        {historial.length > 0 && (
          <div>
            <h2 className="text-2xl font-heading font-bold mb-4">Historial</h2>
            <div className="grid gap-4">
              {historial.slice(0, 5).map((solicitud) => (
                <Card key={solicitud.id}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-semibold capitalize">{solicitud.servicio.replace('_', ' ')}</p>
                        <p className="text-sm text-slate-600">{new Date(solicitud.created_at).toLocaleDateString('es-AR')}</p>
                      </div>
                      <div className="text-right">
                        {getEstadoBadge(solicitud.estado)}
                        <p className="text-sm font-semibold text-green-600 mt-1">${solicitud.pago_profesional.toLocaleString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {solicitudes.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <p className="text-slate-500">No tienes solicitudes aún. Espera a que los clientes te contacten.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
