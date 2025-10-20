# Makefile for Ad Video Generator
# Use with: make <command>

.PHONY: help dev dev-build dev-down dev-logs prod prod-build prod-down prod-logs clean backup restore test lint

# Default command
help:
	@echo "Ad Video Generator - Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-build    - Build and start development"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make dev-logs     - View development logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production"
	@echo "  make prod-down    - Stop production environment"
	@echo "  make prod-logs    - View production logs"
	@echo ""
	@echo "Database:"
	@echo "  make backup       - Backup DynamoDB tables (requires AWS CLI)"
	@echo "  make restore      - Restore DynamoDB tables (requires AWS CLI)"
	@echo "  make db-shell     - Open DynamoDB console (opens web browser)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove containers and volumes"
	@echo "  make reset        - Full reset (WARNING: deletes data)"
	@echo "  make ps           - Show running containers"
	@echo "  make stats        - Show container stats"

# Development commands
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev-build:
	docker-compose -f docker-compose.dev.yml up -d --build

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Production commands
prod:
	docker-compose up -d
	@echo ""
	@echo "Production environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"

prod-build:
	docker-compose build --no-cache
	docker-compose up -d

prod-down:
	docker-compose down

prod-logs:
	docker-compose logs -f

# Database commands
backup:
	@echo "Creating DynamoDB table backups..."
	@aws dynamodb create-backup --table-name $(shell grep USERS_TABLE .env | cut -d '=' -f2) --backup-name users-backup-$$(date +%Y%m%d_%H%M%S) --region $(shell grep AWS_REGION .env | cut -d '=' -f2)
	@aws dynamodb create-backup --table-name $(shell grep ADVERTISEMENTS_TABLE .env | cut -d '=' -f2) --backup-name ads-backup-$$(date +%Y%m%d_%H%M%S) --region $(shell grep AWS_REGION .env | cut -d '=' -f2)
	@echo "DynamoDB backups created!"

restore:
	@echo "DynamoDB restore requires manual intervention via AWS Console or CLI"
	@echo "Use: aws dynamodb restore-table-from-backup --backup-arn <backup-arn> --target-table-name <new-table-name>"

db-shell:
	@echo "Opening DynamoDB console in web browser..."
	@open https://console.aws.amazon.com/dynamodb/home || echo "Please open https://console.aws.amazon.com/dynamodb/home manually"

# Container management
ps:
	docker-compose ps

stats:
	docker stats --no-stream

logs:
	docker-compose logs --tail=100

# Maintenance commands
clean:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down
	@echo "Containers stopped and removed"

reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		docker-compose -f docker-compose.dev.yml down -v; \
		docker system prune -f; \
		echo "Full reset completed!"; \
	else \
		echo "Reset cancelled"; \
	fi

# Testing (when tests are added)
test:
	@echo "Running tests..."
	docker exec adgen-backend pytest
	cd frontend && npm test

# Code quality
lint:
	@echo "Running linters..."
	docker exec adgen-backend black app/ --check
	docker exec adgen-backend flake8 app/
	cd frontend && npm run lint
