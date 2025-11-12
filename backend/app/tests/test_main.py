import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app, generar_producto, generar_factura, PRODUCTOS_HACEB

client = TestClient(app)


class TestEndpoints:
    """Pruebas para los endpoints de la API"""
    
    def test_root_endpoint(self):
        """Prueba el endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Prueba el endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "backend-facturas"
    
    def test_obtener_factura_exitoso(self):
        """Prueba obtener una factura con número válido"""
        numero_factura = "FAC-001"
        response = client.get(f"/facturas/v1/{numero_factura}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["numero_factura"] == numero_factura
        assert "fecha" in data
        assert "cliente_nombre" in data
        assert "cliente_documento" in data
        assert "cliente_direccion" in data
        assert "cliente_telefono" in data
        assert "cliente_email" in data
        assert "productos" in data
        assert "subtotal" in data
        assert "iva" in data
        assert "total" in data
        
        # Verificar que hay productos
        assert len(data["productos"]) >= 2
        assert len(data["productos"]) <= 6
        
        # Verificar estructura de productos
        for producto in data["productos"]:
            assert "codigo" in producto
            assert "nombre" in producto
            assert "categoria" in producto
            assert "cantidad" in producto
            assert "precio_unitario" in producto
            assert "subtotal" in producto
    
    def test_obtener_factura_con_diferentes_numeros(self):
        """Prueba que diferentes números de factura devuelven respuestas exitosas"""
        numeros = ["001", "ABC-123", "FAC-2024-001", "12345"]
        
        for numero in numeros:
            response = client.get(f"/facturas/v1/{numero}")
            assert response.status_code == 200
            data = response.json()
            assert data["numero_factura"] == numero
    
    def test_validacion_totales(self):
        """Prueba que los cálculos de totales sean correctos"""
        response = client.get("/facturas/v1/TEST-001")
        assert response.status_code == 200
        
        data = response.json()
        
        # Calcular subtotal manualmente
        subtotal_calculado = sum(p["subtotal"] for p in data["productos"])
        assert abs(data["subtotal"] - subtotal_calculado) < 0.01
        
        # Verificar IVA (19%)
        iva_calculado = subtotal_calculado * 0.19
        assert abs(data["iva"] - iva_calculado) < 0.01
        
        # Verificar total
        total_calculado = subtotal_calculado + iva_calculado
        assert abs(data["total"] - total_calculado) < 0.01
    
    def test_productos_son_haceb(self):
        """Prueba que todos los productos son de la marca Haceb"""
        response = client.get("/facturas/v1/TEST-HACEB")
        assert response.status_code == 200
        
        data = response.json()
        
        for producto in data["productos"]:
            assert "Haceb" in producto["nombre"]
            assert producto["codigo"].startswith("HAC-")
    
    def test_endpoint_inexistente(self):
        """Prueba acceso a endpoint que no existe"""
        response = client.get("/endpoint/inexistente")
        assert response.status_code == 404


class TestGeneradores:
    """Pruebas para las funciones generadoras"""
    
    def test_generar_producto(self):
        """Prueba la generación de un producto"""
        producto = generar_producto()
        
        assert producto.codigo.startswith("HAC-")
        assert len(producto.codigo) == 8  # HAC-XXXX
        assert "Haceb" in producto.nombre
        assert producto.cantidad >= 1
        assert producto.cantidad <= 5
        assert producto.precio_unitario > 0
        assert producto.subtotal == producto.cantidad * producto.precio_unitario
        
        # Verificar que el producto existe en la lista
        nombres_productos = [p["nombre"] for p in PRODUCTOS_HACEB]
        assert producto.nombre in nombres_productos
    
    def test_generar_factura(self):
        """Prueba la generación de una factura completa"""
        numero = "TEST-FACTURA-001"
        factura = generar_factura(numero)
        
        assert factura.numero_factura == numero
        assert factura.fecha is not None
        assert factura.cliente_nombre is not None
        assert len(factura.cliente_documento) == 8
        assert factura.cliente_documento.isdigit()
        assert factura.cliente_direccion is not None
        assert factura.cliente_telefono is not None
        assert "@" in factura.cliente_email
        
        # Verificar productos
        assert len(factura.productos) >= 2
        assert len(factura.productos) <= 6
        
        # Verificar totales
        assert factura.subtotal > 0
        assert factura.iva > 0
        assert factura.total > 0
        assert factura.total == factura.subtotal + factura.iva
    
    def test_productos_tienen_variedad(self):
        """Prueba que se generan diferentes productos"""
        productos_generados = set()
        
        for _ in range(20):
            producto = generar_producto()
            productos_generados.add(producto.nombre)
        
        # Debe haber al menos 3 productos diferentes en 20 intentos
        assert len(productos_generados) >= 3
    
    def test_precios_en_rango_correcto(self):
        """Prueba que los precios están en el rango esperado para cada producto"""
        for _ in range(10):
            producto = generar_producto()
            
            # Buscar el producto base
            producto_base = next(
                (p for p in PRODUCTOS_HACEB if p["nombre"] == producto.nombre),
                None
            )
            
            assert producto_base is not None
            assert producto.precio_unitario >= producto_base["precio_min"]
            assert producto.precio_unitario <= producto_base["precio_max"]


class TestValidaciones:
    """Pruebas de validaciones y manejo de errores"""
    
    def test_estructura_productos_haceb(self):
        """Prueba que la lista de productos Haceb tiene la estructura correcta"""
        assert len(PRODUCTOS_HACEB) > 0
        
        for producto in PRODUCTOS_HACEB:
            assert "nombre" in producto
            assert "categoria" in producto
            assert "precio_min" in producto
            assert "precio_max" in producto
            assert "Haceb" in producto["nombre"]
            assert producto["precio_min"] > 0
            assert producto["precio_max"] > producto["precio_min"]
    
    def test_categorias_productos(self):
        """Prueba que existen diferentes categorías de productos"""
        categorias = set(p["categoria"] for p in PRODUCTOS_HACEB)
        
        # Debe haber al menos 4 categorías diferentes
        assert len(categorias) >= 4
        
        # Verificar algunas categorías esperadas
        categorias_esperadas = ["Refrigeración", "Lavado", "Cocción"]
        for cat in categorias_esperadas:
            assert cat in categorias


class TestIntegracion:
    """Pruebas de integración end-to-end"""
    
    def test_flujo_completo_factura(self):
        """Prueba el flujo completo de obtención de factura"""
        # 1. Verificar que el servicio está activo
        health = client.get("/health")
        assert health.status_code == 200
        
        # 2. Obtener información del API
        root = client.get("/")
        assert root.status_code == 200
        
        # 3. Generar una factura
        response = client.get("/facturas/v1/INTEGRACION-001")
        assert response.status_code == 200
        
        factura = response.json()
        
        # 4. Validar estructura completa
        assert factura["numero_factura"] == "INTEGRACION-001"
        assert len(factura["productos"]) > 0
        
        # 5. Validar que todos los cálculos son correctos
        subtotal_real = sum(p["subtotal"] for p in factura["productos"])
        assert abs(factura["subtotal"] - subtotal_real) < 0.01
        
        iva_real = subtotal_real * 0.19
        assert abs(factura["iva"] - iva_real) < 0.01
        
        total_real = subtotal_real + iva_real
        assert abs(factura["total"] - total_real) < 0.01
    
    def test_multiples_facturas_diferentes(self):
        """Prueba que múltiples llamadas generan datos diferentes"""
        facturas = []
        
        for i in range(5):
            response = client.get(f"/facturas/v1/MULTI-{i}")
            assert response.status_code == 200
            facturas.append(response.json())
        
        # Verificar que los clientes son diferentes
        nombres_clientes = [f["cliente_nombre"] for f in facturas]
        # Al menos algunos nombres deben ser diferentes
        assert len(set(nombres_clientes)) > 1
