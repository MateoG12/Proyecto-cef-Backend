# Imagen base ligera de Python
FROM python:3.11

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Puerto expuesto (el mismo que usa FastAPI por defecto)
EXPOSE 8881

# Comando para iniciar la app
CMD ["uvicorn", "vista:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]