FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorio para reportes
RUN mkdir -p /app/reportes

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8004

# Comando para ejecutar el servicio
CMD ["python", "main.py"]

