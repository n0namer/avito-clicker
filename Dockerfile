FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY avito_clicker ./avito_clicker
RUN python -m pip install --no-cache-dir . && python -m playwright install --with-deps chromium

VOLUME ["/app/storage"]
ENTRYPOINT ["python", "-m", "avito_clicker"]
CMD ["doctor"]
