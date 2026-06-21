# =============================================================================
# Dockerfile multi-stage para el microservicio Task Manager API
# =============================================================================
# Etapa 1 (builder): instala las dependencias en un directorio aislado.
# Etapa 2 (runtime): imagen final mínima, solo con lo necesario para ejecutar.
# Esto reduce el tamaño de la imagen y mejora la seguridad.
# =============================================================================

# ----------------------------- Etapa builder --------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Evita archivos .pyc y fuerza salida sin buffer (logs en tiempo real).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependencias en un prefijo aislado (/install) para copiarlo luego.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ----------------------------- Etapa runtime --------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=Local

# Crea un usuario sin privilegios para no ejecutar como root (buena práctica).
RUN useradd --create-home --uid 1000 appuser

# Copia las dependencias ya instaladas desde la etapa builder.
COPY --from=builder /install /usr/local

# Copia el código de la aplicación.
COPY app ./app

USER appuser

EXPOSE 8000

# Healthcheck a nivel de contenedor (complementa las probes de Kubernetes).
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else sys.exit(1)"

# Arranca el servidor ASGI.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
