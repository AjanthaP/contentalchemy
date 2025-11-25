# Start Redis for ContentAlchemy
Write-Host "Starting Redis server..." -ForegroundColor Cyan

# Check if container already exists
$existingContainer = docker ps -a --filter "name=contentalchemy-redis" --format "{{.Names}}" 2>$null

if ($existingContainer -eq "contentalchemy-redis") {
    Write-Host "Redis container already exists. Starting it..." -ForegroundColor Yellow
    docker start contentalchemy-redis
} else {
    Write-Host "Creating new Redis container..." -ForegroundColor Green
    docker run -d --name contentalchemy-redis -p 6379:6379 redis:7-alpine
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Redis is running on localhost:6379" -ForegroundColor Green
    Write-Host ""
    Write-Host "To connect: redis://localhost:6379" -ForegroundColor Cyan
    Write-Host "To stop: docker stop contentalchemy-redis" -ForegroundColor Gray
} else {
    Write-Host "✗ Failed to start Redis. Make sure Docker Desktop is running." -ForegroundColor Red
    Write-Host "You can still use the application with file-based storage." -ForegroundColor Yellow
}
