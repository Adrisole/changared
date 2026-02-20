import requests
import sys
import json
from datetime import datetime

class ChangaRedAPITester:
    def __init__(self, base_url="https://changared-services.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.cliente_token = None
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.profesionales_created = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "",
            200
        )
        if success:
            expected_message = "ChangaRed API v1.0"
            if response.get('message') == expected_message and response.get('status') == 'operational':
                print(f"✅ Health check response correct: {response}")
                return True
            else:
                print(f"❌ Health check response incorrect: {response}")
                return False
        return False

    def test_register_cliente(self):
        """Test client registration"""
        success, response = self.run_test(
            "Register Cliente",
            "POST",
            "auth/register",
            200,
            data={
                "email": "cliente@test.com",
                "password": "test123",
                "nombre": "Cliente Test",
                "telefono": "+54 376 123-4567",
                "rol": "cliente"
            }
        )
        if success and 'token' in response:
            self.cliente_token = response['token']
            print(f"✅ Cliente token obtained: {self.cliente_token[:20]}...")
            return True
        return False

    def test_login_cliente(self):
        """Test client login"""
        success, response = self.run_test(
            "Login Cliente",
            "POST",
            "auth/login",
            200,
            data={
                "email": "cliente@test.com",
                "password": "test123"
            }
        )
        if success and 'token' in response:
            self.cliente_token = response['token']
            print(f"✅ Cliente login successful, token: {self.cliente_token[:20]}...")
            return True
        return False

    def test_register_admin(self):
        """Test admin registration"""
        success, response = self.run_test(
            "Register Admin",
            "POST",
            "auth/register",
            200,
            data={
                "email": "admin@changared.com",
                "password": "admin123",
                "nombre": "Admin ChangaRed",
                "telefono": "+54 376 999-9999",
                "rol": "admin"
            }
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"✅ Admin token obtained: {self.admin_token[:20]}...")
            return True
        return False

    def test_create_profesionales(self):
        """Create test professionals"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False

        profesionales_data = [
            {
                "nombre": "Juan Electricista",
                "telefono": "+54 376 111-1111",
                "email": "electricista@test.com",
                "tipo_servicio": "electricista",
                "latitud": -27.370,
                "longitud": -55.900,
                "disponible": True,
                "tarifa_base": 5000
            },
            {
                "nombre": "Pedro Plomero",
                "telefono": "+54 376 222-2222",
                "email": "plomero@test.com",
                "tipo_servicio": "plomero",
                "latitud": -27.375,
                "longitud": -55.905,
                "disponible": True,
                "tarifa_base": 4500
            },
            {
                "nombre": "Carlos Gasista",
                "telefono": "+54 376 333-3333",
                "email": "gasista@test.com",
                "tipo_servicio": "gasista",
                "latitud": -27.380,
                "longitud": -55.910,
                "disponible": True,
                "tarifa_base": 5500
            }
        ]

        all_success = True
        for prof_data in profesionales_data:
            success, response = self.run_test(
                f"Create {prof_data['tipo_servicio']}",
                "POST",
                "profesionales",
                200,
                data=prof_data,
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
            if success:
                self.profesionales_created.append(response)
            else:
                all_success = False

        return all_success

    def test_create_solicitud_urgente(self):
        """Test creating urgent service request with AI processing"""
        if not self.cliente_token:
            print("❌ No cliente token available")
            return False

        success, response = self.run_test(
            "Create Urgent Solicitud (AI Processing)",
            "POST",
            "solicitudes",
            200,
            data={
                "mensaje_cliente": "Se me cortó la luz en toda la casa y necesito un electricista urgente",
                "latitud": -27.365,
                "longitud": -55.896,
                "urgencia": "urgente"
            },
            headers={'Authorization': f'Bearer {self.cliente_token}'}
        )
        
        if success:
            # Validate AI processing results
            print("\n🔍 Validating AI processing results...")
            
            # Check service type detection
            if 'servicio' in response:
                print(f"✅ Service detected: {response['servicio']}")
                if 'electricista' in response['servicio'].lower():
                    print("✅ Correct service type detected (electricista)")
                else:
                    print(f"⚠️  Service type may be incorrect: {response['servicio']}")
            
            # Check urgency pricing (30% surcharge)
            if 'precio_total' in response and 'profesional_id' in response:
                precio_total = response['precio_total']
                print(f"✅ Total price with urgency: ${precio_total}")
                
                # Find the assigned professional's base rate
                for prof in self.profesionales_created:
                    if prof['id'] == response['profesional_id']:
                        expected_price = prof['tarifa_base'] * 1.3  # 30% surcharge
                        if abs(precio_total - expected_price) < 0.01:
                            print(f"✅ Urgency pricing correct: ${precio_total} (base: ${prof['tarifa_base']} + 30%)")
                        else:
                            print(f"❌ Urgency pricing incorrect: got ${precio_total}, expected ${expected_price}")
                        break
            
            # Check commission calculation (20% ChangaRed, 80% professional)
            if 'comision_changared' in response and 'pago_profesional' in response:
                comision = response['comision_changared']
                pago_prof = response['pago_profesional']
                total = response['precio_total']
                
                expected_comision = total * 0.2
                expected_pago = total * 0.8
                
                if abs(comision - expected_comision) < 0.01 and abs(pago_prof - expected_pago) < 0.01:
                    print(f"✅ Commission calculation correct: ChangaRed ${comision:.2f} (20%), Professional ${pago_prof:.2f} (80%)")
                else:
                    print(f"❌ Commission calculation incorrect: ChangaRed ${comision:.2f}, Professional ${pago_prof:.2f}")
            
            # Check AI response message
            if 'mensaje_respuesta' in response:
                print(f"✅ AI response message generated: {response['mensaje_respuesta'][:100]}...")
            
            return True
        return False

    def test_create_solicitud_normal(self):
        """Test creating normal service request"""
        if not self.cliente_token:
            print("❌ No cliente token available")
            return False

        success, response = self.run_test(
            "Create Normal Solicitud",
            "POST",
            "solicitudes",
            200,
            data={
                "mensaje_cliente": "Tengo una fuga de agua en el baño y necesito un plomero",
                "latitud": -27.365,
                "longitud": -55.896,
                "urgencia": "normal"
            },
            headers={'Authorization': f'Bearer {self.cliente_token}'}
        )
        
        if success:
            # Validate normal pricing (no surcharge)
            if 'precio_total' in response and 'profesional_id' in response:
                precio_total = response['precio_total']
                print(f"✅ Normal price: ${precio_total}")
                
                # Find the assigned professional's base rate
                for prof in self.profesionales_created:
                    if prof['id'] == response['profesional_id']:
                        expected_price = prof['tarifa_base']  # No surcharge
                        if abs(precio_total - expected_price) < 0.01:
                            print(f"✅ Normal pricing correct: ${precio_total} (base: ${prof['tarifa_base']})")
                        else:
                            print(f"❌ Normal pricing incorrect: got ${precio_total}, expected ${expected_price}")
                        break
            
            return True
        return False

    def test_get_solicitudes(self):
        """Test getting client's solicitudes"""
        if not self.cliente_token:
            print("❌ No cliente token available")
            return False

        success, response = self.run_test(
            "Get Cliente Solicitudes",
            "GET",
            "solicitudes",
            200,
            headers={'Authorization': f'Bearer {self.cliente_token}'}
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} solicitudes")
            return True
        return False

    def test_admin_metrics(self):
        """Test admin metrics endpoint"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False

        success, response = self.run_test(
            "Admin Metrics",
            "GET",
            "admin/metrics",
            200,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if success:
            required_fields = ['total_solicitudes', 'solicitudes_completadas', 'total_ingresos', 'total_comisiones', 'profesionales_activos']
            all_fields_present = all(field in response for field in required_fields)
            
            if all_fields_present:
                print("✅ All required metrics fields present")
                print(f"   Total solicitudes: {response['total_solicitudes']}")
                print(f"   Completadas: {response['solicitudes_completadas']}")
                print(f"   Total ingresos: ${response['total_ingresos']}")
                print(f"   Total comisiones: ${response['total_comisiones']}")
                print(f"   Profesionales activos: {response['profesionales_activos']}")
                return True
            else:
                print(f"❌ Missing required fields in metrics response")
                return False
        return False

    def test_security_unauthorized_access(self):
        """Test security - unauthorized access"""
        print("\n🔒 Testing Security - Unauthorized Access")
        
        # Test accessing profesionales without token
        success, _ = self.run_test(
            "Access profesionales without token (should fail)",
            "GET",
            "profesionales",
            401
        )
        
        # Test accessing admin metrics with client token
        if self.cliente_token:
            success2, _ = self.run_test(
                "Access admin metrics with client token (should fail)",
                "GET",
                "admin/metrics",
                403,
                headers={'Authorization': f'Bearer {self.cliente_token}'}
            )
            return success and success2
        
        return success

    def test_ai_ambiguous_message(self):
        """Test AI processing with ambiguous message"""
        if not self.cliente_token:
            print("❌ No cliente token available")
            return False

        success, response = self.run_test(
            "AI Processing - Ambiguous Message",
            "POST",
            "solicitudes",
            200,
            data={
                "mensaje_cliente": "Tengo un problema en casa",
                "latitud": -27.365,
                "longitud": -55.896,
                "urgencia": "normal"
            },
            headers={'Authorization': f'Bearer {self.cliente_token}'}
        )
        
        if success:
            print("✅ AI processed ambiguous message and assigned a professional")
            if 'servicio' in response:
                print(f"   Service detected/assigned: {response['servicio']}")
            if 'profesional_nombre' in response:
                print(f"   Professional assigned: {response['profesional_nombre']}")
            return True
        return False

def main():
    print("🚀 Starting ChangaRed API Testing...")
    print("=" * 60)
    
    tester = ChangaRedAPITester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("Register Cliente", tester.test_register_cliente),
        ("Login Cliente", tester.test_login_cliente),
        ("Register Admin", tester.test_register_admin),
        ("Create Profesionales", tester.test_create_profesionales),
        ("Create Urgent Solicitud (AI)", tester.test_create_solicitud_urgente),
        ("Create Normal Solicitud", tester.test_create_solicitud_normal),
        ("Get Solicitudes", tester.test_get_solicitudes),
        ("Admin Metrics", tester.test_admin_metrics),
        ("Security Tests", tester.test_security_unauthorized_access),
        ("AI Ambiguous Message", tester.test_ai_ambiguous_message),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print final results
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n✅ All tests passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())