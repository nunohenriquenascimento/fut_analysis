FROM node:22-bookworm-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV NEXT_PUBLIC_API_URL=/api BUILD_STANDALONE=true NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM caddy:2.10.2 AS proxy
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
ENV APP_ENV=production AUTH_COOKIE_SECURE=true AUTH_COOKIE_SAMESITE=lax
WORKDIR /app/backend
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY --from=frontend-build /usr/local/bin/node /usr/local/bin/node
COPY --from=proxy /usr/bin/caddy /usr/local/bin/caddy
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./
COPY --from=frontend-build /build/.next/standalone /app/frontend
COPY --from=frontend-build /build/.next/static /app/frontend/.next/static
COPY --from=frontend-build /build/public /app/frontend/public
COPY deploy/ /app/deploy/
RUN useradd --create-home --uid 10001 ccdr && chown -R ccdr:ccdr /app/frontend
USER ccdr
EXPOSE 8080
CMD ["python", "/app/deploy/start.py"]
