# Generador de Facturas - Taller 2 LPA2

Autor: Jhon Salcedo  
GitHub: @jasl89

## Descripción

Sistema completo de generación de facturas electrónicas en español, utilizando FastAPI y Flask. El backend genera datos sintéticos de productos electrodomésticos Haceb (neveras, lavadoras, hornos, microondas, televisores, licuadoras, etc.) con Faker. El frontend permite consultar facturas y generar PDFs con ReportLab y Bootstrap.

## Arquitectura

```
┌────────────────┐          ┌───────────────┐
│  Frontend Web  │ ───────> │  Backend API  │
│  puerto 3000   │   HTTP   │  puerto 8000  │
│  Flask + PDF   │ <─────── │  FastAPI + Faker │
└────────────────┘          └───────────────┘
```

## Estructura del Proyecto

```
lpa2-taller2/
├── docker-compose.yml
├── README.md
├── .pre-commit-config.yaml
├── pytest.ini
├── .coveragerc
├── backend/
│   ├── Dockerfile
│   └── app/
│       ├── main.py
│       ├── requirements.txt
│       └── tests/
│           ├── test_main.py
│           └── __init__.py
└── frontend/
    ├── Dockerfile
    └── app/
        ├── main.py
        ├── requirements.txt
        ├── static/
        │   ├── css/
        │   │   └── style.css
        │   └── js/
        │       └── app.js
        └── templates/
            └── index.html
```

## Tecnologías

- Backend: FastAPI, Faker, Uvicorn, Pydantic
- Frontend: Flask, Bootstrap 5, ReportLab
- Testing: pytest, pytest-cov (cobertura mínima 80%)
- Linting: ruff
- Pre-commit hooks: validación de código antes de commits
- Containerización: Docker, Docker Compose

## Instalación y Ejecución

### Prerrequisitos

- Docker
- Docker Compose

### Iniciar el Proyecto

```bash
# Clonar el repositorio
git clone https://github.com/jasl89/lpa2-taller2.git
cd lpa2-taller2

# Construir y levantar los servicios
docker-compose up --build
```

### Acceso

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Backend API

### Endpoints Principales

**GET /** - Información del API

**GET /facturas/v1/{numero_factura}** - Genera una factura con datos sintéticos

**GET /health** - Health check del servicio

### Ejemplo de Respuesta

```json
{
  "numero_factura": "FAC-001",
  "fecha": "2025-11-12 10:30:45",
  "cliente_nombre": "Juan Pérez García",
  "cliente_documento": "45678912",
  "cliente_direccion": "Calle 45 #23-67, Medellín",
  "cliente_telefono": "+57 300 123 4567",
  "cliente_email": "juan.perez@email.com",
  "productos": [
    {
      "codigo": "HAC-1234",
      "nombre": "Nevera Haceb No Frost 350L",
      "categoria": "Refrigeración",
      "cantidad": 2,
      "precio_unitario": 1450000,
      "subtotal": 2900000
    }
  ],
  "subtotal": 2900000,
  "iva": 551000,
  "total": 3451000
}
```

### Productos Electrodomésticos Haceb

El sistema genera facturas con productos reales de Haceb:
- Neveras (Frost y No Frost)
- Lavadoras (12kg y 18kg)
- Estufas y hornos
- Microondas
- Televisores (LED y Smart)
- Licuadoras
- Ventiladores
- Aires acondicionados
- Campanas extractoras
- Calentadores de agua

## Frontend

### Funcionalidades

1. Interfaz web con Bootstrap 5 (colores neutros: grises, blancos y azul suave)
2. Formulario para ingresar número de factura
3. Consulta al backend vía API REST
4. Visualización de datos de la factura
5. Generación y descarga de PDF profesional con ReportLab

### Modificar el Frontend

- `frontend/app/main.py` - Lógica del servidor Flask y generación de PDF
- `frontend/app/templates/index.html` - Interfaz HTML
- `frontend/app/static/css/style.css` - Estilos CSS
- `frontend/app/static/js/app.js` - Lógica JavaScript

## Testing

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest -v

# Ejecutar con cobertura
pytest --cov=backend/app --cov-report=term-missing

# Verificar cobertura mínima (80%)
pytest --cov=backend/app --cov-fail-under=80
```

### Cobertura de Pruebas

Las pruebas incluyen:
- Pruebas de endpoints (éxito y error)
- Validación de cálculos (subtotal, IVA, total)
- Verificación de productos Haceb
- Pruebas de generadores de datos
- Pruebas de integración end-to-end

## Pre-commit Hooks

### Instalación

```bash
# Instalar pre-commit
pip install pre-commit pytest pytest-cov ruff

# Instalar hooks
pre-commit install
```

### Ejecutar Manualmente

```bash
# Ejecutar en todos los archivos
pre-commit run --all-files

# Ejecutar solo ruff
pre-commit run ruff --all-files

# Ejecutar solo pytest
pre-commit run pytest --all-files
```

### Configuración

El archivo `.pre-commit-config.yaml` ejecuta automáticamente:
- ruff: Validación de estilo y corrección automática
- pytest: Ejecución de pruebas con cobertura mínima del 80%

## Docker

### Comandos Útiles

```bash
# Levantar servicios
docker-compose up

# Levantar en segundo plano
docker-compose up -d

# Reconstruir imágenes
docker-compose up --build

# Ver logs
docker-compose logs -f

# Ver logs de un servicio
docker-compose logs -f backend
docker-compose logs -f frontend

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reiniciar un servicio
docker-compose restart backend
```

### Variables de Entorno

Configuradas en `docker-compose.yml`:

```yaml
environment:
  - API_URL=http://backend:8000
  - DEBUG=true
```

## Commits y Control de Versiones

### Convención de Commits

```bash
git add .
git commit -m "feat: agregar endpoint de facturas"
git commit -m "test: agregar pruebas de API"
git commit -m "fix: corregir generación de PDF"
git commit -m "chore: actualizar pre-commit y ruff"
git push origin main
```

### Tipos de Commits

- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `test`: Agregar o modificar pruebas
- `chore`: Tareas de mantenimiento
- `docs`: Documentación
- `style`: Formato de código
- `refactor`: Refactorización

## Uso de la Aplicación

1. Abrir navegador en http://localhost:3000
2. Ingresar número de factura (ej: FAC-2024-001, INV-123, etc.)
3. Hacer clic en "Consultar Factura"
4. Ver detalles de la factura generada
5. Hacer clic en "Descargar PDF" para obtener el documento

## Pruebas del Backend

```bash
# Endpoint raíz
curl http://localhost:8000/

# Generar factura
curl http://localhost:8000/facturas/v1/TEST-001

# Con formato JSON
curl http://localhost:8000/facturas/v1/TEST-001 | jq

# Health check
curl http://localhost:8000/health
```

## Documentación API

Documentación interactiva disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

