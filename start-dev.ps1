# PowerShell script to start Vigen AI development environment

Write-Host "🎬 Vigen AI - Starting Development Environment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "🔍 Checking Docker status..." -ForegroundColor Yellow

try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Write-Host "📋 Copying .env.example to .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file" -ForegroundColor Green
        Write-Host "📝 IMPORTANT: Edit .env file with your AWS credentials before continuing!" -ForegroundColor Red
        Write-Host "Press any key to continue after editing .env..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "❌ No .env.example file found" -ForegroundColor Red
        exit 1
    }
}

# Start development environment
Write-Host "🚀 Starting development services..." -ForegroundColor Yellow

try {
    docker-compose -f docker-compose.dev.yml up -d
    
    Write-Host ""
    Write-Host "✅ Development environment started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "   Crew API:  http://localhost:8001" -ForegroundColor White
    Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Useful commands:" -ForegroundColor Cyan
    Write-Host "   View logs:     docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor White
    Write-Host "   Stop services: docker-compose -f docker-compose.dev.yml down" -ForegroundColor White
    Write-Host "   Or use:        make dev-logs" -ForegroundColor White
    Write-Host "   Or use:        make dev-down" -ForegroundColor White
    Write-Host ""
    
    # Wait for services to be ready
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check service health
    Write-Host "🏥 Checking service health..." -ForegroundColor Yellow
    
    try {
        $backend = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Backend may still be starting up..." -ForegroundColor Yellow
    }
    
    try {
        $crew = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Crew API is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Crew API may still be starting up..." -ForegroundColor Yellow
    }
    
    try {
        $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Frontend is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Frontend may still be starting up..." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 Development environment is ready!" -ForegroundColor Green
    Write-Host "You can now open http://localhost:3000 in your browser" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Failed to start development environment:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}