# 1. Imagen base de Python ligera
FROM python:3.11-slim

# 2. Variables de entorno para optimizar Python en Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos dependencias de sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalamos dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copiamos el resto del código
COPY . /app/

# 7. Comando para iniciar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]