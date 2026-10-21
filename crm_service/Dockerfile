FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
COPY agent agent
COPY tools tools
COPY crm_service crm_service
RUN pip install --no-cache-dir ".[api]"
EXPOSE 8000
CMD ["uvicorn", "crm_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
