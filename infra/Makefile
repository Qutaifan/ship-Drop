.PHONY: help up down logs ps migrate admin backup validate selftest

help:
	@echo "up        bring the stack up (build if needed)"
	@echo "down      stop the stack, keep volumes"
	@echo "logs      follow all logs"
	@echo "migrate   run Medusa migrations"
	@echo "admin     create an admin user"
	@echo "backup    dump Postgres database and sync to Cloudflare R2"
	@echo "validate  run the pipeline + infra/docs validators"
	@echo "selftest  prove the validators fail correctly on broken input"

up:
	docker compose --env-file .env up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

migrate:
	docker compose exec medusa-server npx medusa db:migrate

admin:
	docker compose exec medusa-server npx medusa user -e $(EMAIL) -p $(PASSWORD)

backup:
	bash backup_r2.sh

validate:
	python3 ../scripts/validate_workspace.py ..
	python3 ../scripts/validate_infra.py ..

selftest:
	python3 ../scripts/selftest.py
