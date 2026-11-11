FROM python:3.11-slim

# Trabajamos desde /app dentro del contenedor.
WORKDIR /app

# Mantiene los logs visibles y evita archivos .pyc innecesarios.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos las dependencias antes de copiar el código.
# Docker puede reutilizar esta capa si requirements.txt no cambió.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos los clientes y el simulador.
# No copiamos .venv: el contenedor tiene su propio Python.
COPY app ./app
COPY carga ./carga

# Al iniciar el contenedor, ejecuta el simulador.
CMD ["python", "carga/simular_carga.py"]
