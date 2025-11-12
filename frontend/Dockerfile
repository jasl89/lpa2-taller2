# Imagen base oficial de Python
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements primero (mejor cache de Docker)
COPY ./app/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY ./app .

# Exponer puerto
EXPOSE 3000

# Comando de arranque con modo debug para desarrollo
CMD ["python", "main.py"]

