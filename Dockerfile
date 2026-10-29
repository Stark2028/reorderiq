FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LOKY_MAX_CPU_COUNT=1
WORKDIR /app
COPY requirements.runtime.lock ./
RUN pip install --no-cache-dir -r requirements.runtime.lock
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --no-deps . && useradd --uid 10001 --create-home app
USER 10001:10001
EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 CMD python -c "import json, urllib.request; assert json.load(urllib.request.urlopen('http://127.0.0.1:8010/api/status', timeout=8))['ready']"
CMD ["python", "-m", "reorderiq.cli", "serve", "--runs-dir", "/artifacts", "--host", "0.0.0.0", "--port", "8010"]
