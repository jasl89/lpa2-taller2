from datetime import datetime
from typing import List

from faker import Faker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Generador de Facturas API",
    description="API para generar facturas con datos sintéticos de electrodomésticos Haceb",
    version="1.0.0"
)

fake = Faker(['es_ES', 'es_MX'])

# Lista de productos electrodomésticos Haceb
PRODUCTOS_HACEB = [
    {"nombre": "Nevera Haceb Frost 250L", "categoria": "Refrigeración", "precio_min": 800000, "precio_max": 1500000},
    {"nombre": "Nevera Haceb No Frost 350L", "categoria": "Refrigeración", "precio_min": 1200000, "precio_max": 2000000},
    {"nombre": "Lavadora Haceb 12kg Digital", "categoria": "Lavado", "precio_min": 900000, "precio_max": 1600000},
    {"nombre": "Lavadora Haceb 18kg Carga Superior", "categoria": "Lavado", "precio_min": 1100000, "precio_max": 1800000},
    {"nombre": "Estufa Haceb 4 Puestos", "categoria": "Cocción", "precio_min": 400000, "precio_max": 800000},
    {"nombre": "Horno Microondas Haceb 1.1 pies", "categoria": "Cocción", "precio_min": 250000, "precio_max": 500000},
    {"nombre": "Horno Eléctrico Haceb 42L", "categoria": "Cocción", "precio_min": 300000, "precio_max": 600000},
    {"nombre": "Televisor Haceb LED 43 pulgadas", "categoria": "Entretenimiento", "precio_min": 800000, "precio_max": 1300000},
    {"nombre": "Televisor Haceb Smart 55 pulgadas", "categoria": "Entretenimiento", "precio_min": 1200000, "precio_max": 2000000},
    {"nombre": "Licuadora Haceb 1.5L", "categoria": "Pequeños electrodomésticos", "precio_min": 80000, "precio_max": 150000},
    {"nombre": "Ventilador Haceb de Pie", "categoria": "Climatización", "precio_min": 100000, "precio_max": 200000},
    {"nombre": "Aire Acondicionado Haceb 12000 BTU", "categoria": "Climatización", "precio_min": 1000000, "precio_max": 1800000},
    {"nombre": "Campana Extractora Haceb 60cm", "categoria": "Cocción", "precio_min": 300000, "precio_max": 600000},
    {"nombre": "Calentador de Agua Haceb 30L", "categoria": "Calentamiento", "precio_min": 400000, "precio_max": 700000},
]


class Producto(BaseModel):
    codigo: str
    nombre: str
    categoria: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class Factura(BaseModel):
    numero_factura: str
    fecha: str
    cliente_nombre: str
    cliente_documento: str
    cliente_direccion: str
    cliente_telefono: str
    cliente_email: str
    productos: List[Producto]
    subtotal: float
    iva: float
    total: float


def generar_producto():
    """Genera un producto aleatorio de electrodomésticos Haceb"""
    producto_base = fake.random_element(PRODUCTOS_HACEB)
    cantidad = fake.random_int(min=1, max=5)
    precio_unitario = fake.random_int(
        min=producto_base["precio_min"],
        max=producto_base["precio_max"]
    )
    subtotal = cantidad * precio_unitario
    
    return Producto(
        codigo=f"HAC-{fake.random_int(min=1000, max=9999)}",
        nombre=producto_base["nombre"],
        categoria=producto_base["categoria"],
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        subtotal=subtotal
    )


def generar_factura(numero_factura: str):
    """Genera una factura completa con datos sintéticos"""
    # Generar entre 2 y 6 productos
    num_productos = fake.random_int(min=2, max=6)
    productos = [generar_producto() for _ in range(num_productos)]
    
    # Calcular totales
    subtotal = sum(p.subtotal for p in productos)
    iva = subtotal * 0.19  # IVA del 19%
    total = subtotal + iva
    
    return Factura(
        numero_factura=numero_factura,
        fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        cliente_nombre=fake.name(),
        cliente_documento=str(fake.random_int(min=10000000, max=99999999)),
        cliente_direccion=fake.address().replace('\n', ', '),
        cliente_telefono=fake.phone_number(),
        cliente_email=fake.email(),
        productos=productos,
        subtotal=subtotal,
        iva=iva,
        total=total
    )


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "mensaje": "API Generador de Facturas Haceb",
        "version": "1.0.0",
        "endpoints": {
            "facturas": "/facturas/v1/{numero_factura}",
            "documentacion": "/docs"
        }
    }


@app.get("/facturas/v1/{numero_factura}", response_model=Factura)
async def obtener_factura(numero_factura: str):
    """
    Genera y devuelve una factura con datos sintéticos
    
    - **numero_factura**: Número de factura (puede ser cualquier string)
    """
    if not numero_factura or len(numero_factura.strip()) == 0:
        raise HTTPException(status_code=400, detail="El número de factura no puede estar vacío")
    
    try:
        factura = generar_factura(numero_factura)
        return factura
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la factura: {str(e)}")


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {"status": "ok", "service": "backend-facturas"}

