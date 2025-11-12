REG=ghcr.io/oounis
IMG=$(REG)/coreon-edu-api:latest

api-ship:
\tdocker build -t $(IMG) .
\tdocker push $(IMG)

infra-restart:
\tcd ~/kogia/coreon-edu-infra && docker compose pull && docker compose up -d && docker compose ps

db-sync:
\tcd ~/kogia/coreon-edu-infra && docker compose exec -T api python - <<'PY'\nfrom app.db.session import Base, engine\nfrom app import models\nBase.metadata.create_all(bind=engine)\nprint("✅ DB synced")\nPY

refresh-api: api-ship infra-restart db-sync
\t@echo "✅ refresh complete"
