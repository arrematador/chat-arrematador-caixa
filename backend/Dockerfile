FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Gunicorn com múltiplos workers para alta concorrência
# Workers = 2 * CPU + 1 (Render Starter tem 0.5-1 CPU, então 2-3 workers)
CMD ["gunicorn", "main:app", \
     "-w", "3", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
