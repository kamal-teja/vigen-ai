# PowerShell script to start Vigen AI production environment

Write-Host "🎬 Vigen AI - Starting Production Environment" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

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
    Write-Host "❌ .env file is required for production" -ForegroundColor Red
    Write-Host "Please create .env file with your production configuration" -ForegroundColor Yellow
    exit 1
}

# Confirmation for production deployment
Write-Host "⚠️  You are about to start the PRODUCTION environment" -ForegroundColor Yellow
Write-Host "Make sure your .env file contains production-ready configuration" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to cancel, or any key to continue..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Start production environment
Write-Host "🚀 Starting production services..." -ForegroundColor Yellow

try {
    docker-compose up -d --build
    
    Write-Host ""
    Write-Host "✅ Production environment started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "   Crew API:  http://localhost:8001" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Management commands:" -ForegroundColor Cyan
    Write-Host "   View logs:     docker-compose logs -f" -ForegroundColor White
    Write-Host "   Stop services: docker-compose down" -ForegroundColor White
    Write-Host "   Or use:        make prod-logs" -ForegroundColor White
    Write-Host "   Or use:        make prod-down" -ForegroundColor White
    Write-Host ""
    
    # Wait for services to be ready
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Check service health
    Write-Host "🏥 Checking service health..." -ForegroundColor Yellow
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop | Out-Null
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Backend health check failed - may still be starting" -ForegroundColor Yellow
    }
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 10 -ErrorAction Stop | Out-Null
        Write-Host "✅ Crew API is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Crew API health check failed - may still be starting" -ForegroundColor Yellow
    }
    
    try {
        Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -ErrorAction Stop | Out-Null
        Write-Host "✅ Frontend is healthy" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Frontend health check failed - may still be starting" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 Production environment is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔐 Security reminders:" -ForegroundColor Yellow
    Write-Host "   - Ensure your SECRET_KEY is strong and secure" -ForegroundColor White
    Write-Host "   - Verify AWS credentials have minimal required permissions" -ForegroundColor White
    Write-Host "   - Monitor logs for any security issues" -ForegroundColor White
    Write-Host "   - Set up proper SSL/TLS termination if serving publicly" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to start production environment:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}