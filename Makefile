REG=ghcr.io/oounis
IMG=$(REG)/coreon-edu-api:latest

api-ship:
	@echo "🚀 Building & pushing API..."
	docker build -t $(IMG) .
	docker push $(IMG)

infra-restart:
	@echo "♻️ Restarting infrastructure..."
	cd ~/kogia/coreon-edu-infra && docker compose pull && docker compose up -d && docker compose ps

db-sync:
	@echo "🗄️  Syncing database models..."
	cd ~/kogia/coreon-edu-infra && docker compose exec -T api python3 -c "from app.db.session import Base, engine; from app import models; Base.metadata.create_all(bind=engine); print('✅ DB synced')"

refresh-api: api-ship infra-restart db-sync
	@echo "✅ Refresh complete!"
