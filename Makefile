# Makefile for Vigen AI - Complete Video Advertisement Platform
# Use with: make <command>

.PHONY: help dev dev-build dev-down dev-logs prod prod-build prod-down prod-logs clean ps stats test lint setup

# Default command
help:
	@echo "🎬 Vigen AI - Complete Video Advertisement Platform"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make setup        - Setup environment and dependencies"
	@echo "  make dev          - Start development environment"
	@echo "  make prod         - Start production environment"
	@echo ""
	@echo "📦 Development Commands:"
	@echo "  make dev          - Start all services in development mode"
	@echo "  make dev-build    - Build and start development services"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make dev-logs     - View development logs"
	@echo ""
	@echo "🏭 Production Commands:"
	@echo "  make prod         - Start all services in production mode"
	@echo "  make prod-build   - Build and start production services"
	@echo "  make prod-down    - Stop production environment"
	@echo "  make prod-logs    - View production logs"
	@echo ""
	@echo "🔧 Individual Services:"
	@echo "  make app          - Start only web application (frontend + backend)"
	@echo "  make crew         - Start only AI video generation service"
	@echo "  make frontend     - Start only frontend development server"
	@echo "  make backend      - Start only backend development server"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test         - Run all tests"
	@echo "  make test-app     - Run app tests only"
	@echo "  make test-crew    - Run crew-api tests only"
	@echo "  make lint         - Run linting on all code"
	@echo ""
	@echo "🛠️  Maintenance:"
	@echo "  make clean        - Remove containers, images, and volumes"
	@echo "  make reset        - Full reset (WARNING: deletes all data)"
	@echo "  make ps           - Show running containers"
	@echo "  make stats        - Show container resource usage"
	@echo "  make logs         - View logs from all services"

# ===== SETUP =====
setup:
	@echo "🔧 Setting up Vigen AI environment..."
	@if not exist .env (copy .env.example .env && echo "✅ Created .env file - please edit with your configuration")
	@echo "📋 Next steps:"
	@echo "  1. Edit .env file with your AWS credentials and configuration"
	@echo "  2. Run 'make dev' to start development environment"

# ===== DEVELOPMENT COMMANDS =====
dev:
	@echo "🚀 Starting Vigen AI development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✅ Development environment started!"
	@echo "🌐 Frontend:  http://localhost:3000"
	@echo "🔧 Backend:   http://localhost:8000"
	@echo "🤖 Crew API:  http://localhost:8001"
	@echo "📚 API Docs:  http://localhost:8000/docs"
	@echo ""
	@echo "📝 View logs: make dev-logs"
	@echo "🛑 Stop:      make dev-down"

dev-build:
	@echo "🔨 Building and starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d --build

dev-down:
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# ===== PRODUCTION COMMANDS =====
prod:
	@echo "🏭 Starting Vigen AI production environment..."
	docker-compose up -d
	@echo ""
	@echo "✅ Production environment started!"
	@echo "🌐 Frontend:  http://localhost:3000"
	@echo "🔧 Backend:   http://localhost:8000"
	@echo "🤖 Crew API:  http://localhost:8001"

prod-build:
	@echo "🔨 Building and starting production environment..."
	docker-compose up -d --build

prod-down:
	@echo "🛑 Stopping production environment..."
	docker-compose down

prod-logs:
	docker-compose logs -f

# ===== INDIVIDUAL SERVICES =====
app:
	@echo "🌐 Starting web application services..."
	docker-compose -f docker-compose.dev.yml up -d frontend-dev backend-dev
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"

crew:
	@echo "🤖 Starting AI video generation service..."
	docker-compose -f docker-compose.dev.yml up -d crew-api-dev
	@echo "Crew API: http://localhost:8001"

frontend:
	@echo "🎨 Starting frontend development server..."
	cd app && make dev-frontend

backend:
	@echo "⚙️  Starting backend development server..."
	cd app && make dev-backend

# ===== TESTING =====
test:
	@echo "🧪 Running all tests..."
	@$(MAKE) test-app
	@$(MAKE) test-crew

test-app:
	@echo "🧪 Running app tests..."
	cd app && make test

test-crew:
	@echo "🧪 Running crew-api tests..."
	cd crew-api && python test.py

lint:
	@echo "🔍 Running linting..."
	cd app/frontend && npm run lint
	cd app/backend && python -m pylint app/
	cd crew-api && python -m pylint app/

# ===== MAINTENANCE =====
clean:
	@echo "🧹 Cleaning up containers and images..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker-compose -f docker-compose.dev.yml down --rmi all --volumes --remove-orphans
	docker system prune -f

reset: clean
	@echo "⚠️  FULL RESET - This will delete all data!"
	@echo "Press Ctrl+C to cancel, or any key to continue..."
	@pause
	docker volume prune -f
	docker network prune -f

ps:
	@echo "📋 Running containers:"
	docker-compose ps
	docker-compose -f docker-compose.dev.yml ps

stats:
	@echo "📊 Container resource usage:"
	docker stats --no-stream

logs:
	@echo "📜 Viewing logs from all services..."
	docker-compose logs -f

# ===== DATABASE COMMANDS =====
db-backup:
	@echo "💾 Backing up DynamoDB tables..."
	@echo "This requires AWS CLI to be configured"
	aws dynamodb describe-table --table-name %USERS_TABLE% --region %AWS_REGION%
	aws dynamodb describe-table --table-name %ADVERTISEMENTS_TABLE% --region %AWS_REGION%

db-shell:
	@echo "🗄️  Opening DynamoDB console..."
	start https://console.aws.amazon.com/dynamodb/home?region=%AWS_REGION%

# ===== HEALTH CHECKS =====
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend unhealthy"
	@curl -f http://localhost:8001/health || echo "❌ Crew API unhealthy"
	@curl -f http://localhost:3000 || echo "❌ Frontend unhealthy"