import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Zap, Droplets, Flame, MapPin, Clock, Shield, CheckCircle, Wind, Tv, Refrigerator, WashingMachine } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative h-[600px] bg-gradient-to-br from-blue-600 via-blue-700 to-slate-800 overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <img 
            src="https://images.pexels.com/photos/257736/pexels-photo-257736.jpeg" 
            alt="Professional service" 
            className="w-full h-full object-cover"
          />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/90 to-transparent"></div>
        
        <div className="relative max-w-7xl mx-auto px-6 h-full flex items-center">
          <div className="max-w-2xl text-white">
            <img 
              src="https://customer-assets.emergentagent.com/job_1ccdb137-8865-4cb4-b134-9dea2c01f7a6/artifacts/klhc20tm_ChangaRed_Logo_IG_320x320%20-%20Editado.png" 
              alt="ChangaRed Logo" 
              className="h-24 mb-6"
              data-testid="hero-logo"
            />
            <h1 className="text-5xl md:text-6xl font-heading font-bold mb-6 leading-tight" data-testid="hero-title">
              Profesionales en minutos, con IA
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100" data-testid="hero-subtitle">
              Electricistas, plomeros y gasistas cerca de ti. Asignación automática, precios transparentes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/auth">
                <Button size="lg" className="text-lg px-8 py-6 w-full sm:w-auto" data-testid="cta-solicitar-button">
                  Solicitar Servicio Ahora
                </Button>
              </Link>
              <Link to="/auth">
                <Button size="lg" variant="outline" className="text-lg px-8 py-6 bg-white/10 border-white/30 text-white hover:bg-white/20 w-full sm:w-auto" data-testid="cta-profesional-button">
                  Soy Profesional
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Servicios Section */}
      <div className="py-20 bg-slate-50" data-testid="servicios-section">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-4xl font-heading font-bold text-center mb-4">Servicios Disponibles</h2>
          <p className="text-center text-slate-600 mb-12 text-lg">Profesionales verificados para emergencias y trabajos programados</p>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="group hover:shadow-xl transition-all duration-300 border-l-4 border-l-primary" data-testid="servicio-electricista-card">
              <CardContent className="p-8">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 group-hover:bg-primary group-hover:scale-110 transition-all">
                  <Zap className="h-8 w-8 text-primary group-hover:text-white" />
                </div>
                <h3 className="text-2xl font-heading font-bold mb-3">Electricista</h3>
                <p className="text-slate-600 mb-4">Instalaciones, reparaciones y emergencias eléctricas. Servicio rápido y seguro.</p>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Instalaciones</li>
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Reparaciones</li>
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Emergencias 24/7</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 border-l-4 border-l-primary" data-testid="servicio-plomero-card">
              <CardContent className="p-8">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 group-hover:bg-primary group-hover:scale-110 transition-all">
                  <Droplets className="h-8 w-8 text-primary group-hover:text-white" />
                </div>
                <h3 className="text-2xl font-heading font-bold mb-3">Plomero</h3>
                <p className="text-slate-600 mb-4">Reparación de cañerías, fugas y sistemas sanitarios. Expertos en agua.</p>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Fugas y goteras</li>
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Cañerías</li>
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Sistemas sanitarios</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 border-l-4 border-l-primary" data-testid="servicio-gasista-card">
              <CardContent className="p-8">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 group-hover:bg-primary group-hover:scale-110 transition-all">
                  <Flame className="h-8 w-8 text-primary group-hover:text-white" />
                </div>
                <h3 className="text-2xl font-heading font-bold mb-3">Gasista</h3>
                <p className="text-slate-600 mb-4">Instalaciones y reparaciones de gas. Seguridad garantizada por profesionales.</p>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Instalaciones</li>
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Inspecciones</li>
                  <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-600" /> Reparaciones seguras</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Cómo Funciona Section */}
      <div className="py-20 bg-white" data-testid="como-funciona-section">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-4xl font-heading font-bold text-center mb-4">¿Cómo Funciona?</h2>
          <p className="text-center text-slate-600 mb-12 text-lg">Tecnología de IA para conectarte con el profesional perfecto</p>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center" data-testid="paso-1">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl font-bold text-primary">
                1
              </div>
              <h3 className="text-xl font-heading font-bold mb-3">Describe tu Problema</h3>
              <p className="text-slate-600">Cuentanos qué necesitas. Nuestra IA entiende tu solicitud.</p>
            </div>

            <div className="text-center" data-testid="paso-2">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <MapPin className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-heading font-bold mb-3">Asignación Automática</h3>
              <p className="text-slate-600">Encontramos al profesional más cercano y disponible.</p>
            </div>

            <div className="text-center" data-testid="paso-3">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Clock className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-heading font-bold mb-3">Precio Transparente</h3>
              <p className="text-slate-600">Conoce el precio antes de confirmar. Sin sorpresas.</p>
            </div>

            <div className="text-center" data-testid="paso-4">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-heading font-bold mb-3">Servicio Seguro</h3>
              <p className="text-slate-600">Profesionales verificados. Satisfacción garantizada.</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Final Section */}
      <div className="py-20 bg-primary text-white" data-testid="cta-final-section">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-heading font-bold mb-6">
            ¿Necesitas un profesional ahora?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Únete a ChangaRed y recibe ayuda en minutos
          </p>
          <Link to="/auth">
            <Button size="lg" variant="outline" className="text-lg px-12 py-6 bg-white text-primary hover:bg-slate-100" data-testid="cta-final-button">
              Empezar Ahora
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p>© 2026 ChangaRed. Todos los derechos reservados.</p>
          <p className="text-sm mt-2">Conectando profesionales con clientes de forma inteligente</p>
        </div>
      </footer>
    </div>
  );
}