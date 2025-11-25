# Redis Setup Guide for ContentAlchemy

## Current Status
✓ Redis Python client installed (redis==5.0.4)
✓ Configuration files updated
✓ Redis helper module created

## Starting Redis

### Option 1: Using Docker (Recommended)

1. **Ensure Docker Desktop is running**
   - Open Docker Desktop from Start Menu
   - Wait for it to fully start (whale icon turns steady)

2. **Run the Redis container**
   ```powershell
   docker run -d --name contentalchemy-redis -p 6379:6379 redis:7-alpine
   ```

3. **Verify Redis is running**
   ```powershell
   docker ps | Select-String "contentalchemy-redis"
   ```

### Option 2: Quick Start Script

```powershell
# From project root
.\start-redis.ps1
```

### Option 3: Manual Docker Commands

```powershell
# Start existing container
docker start contentalchemy-redis

# Or create new container
docker run -d --name contentalchemy-redis -p 6379:6379 redis:7-alpine

# Check logs
docker logs contentalchemy-redis

# Stop container
docker stop contentalchemy-redis

# Remove container
docker rm contentalchemy-redis
```

## Enabling Redis in Your Application

Add to your `.env` file:
```env
USE_REDIS=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Testing Redis Connection

```python
from src.integrations.redis_client import redis_client

# Check if Redis is available
if redis_client.is_available:
    print("✓ Redis is connected")
else:
    print("✗ Redis not available, using file storage")
```

## Benefits of Using Redis

- **Faster Response Times**: Cache frequently accessed data
- **Session Management**: Better handling of user sessions
- **Scalability**: Easy to scale horizontally
- **Real-time Features**: Support for pub/sub patterns

## Fallback Behavior

If Redis is not available, the application automatically falls back to file-based storage in the `data/` directory. No functionality is lost!

## Troubleshooting

1. **Docker not starting**
   - Make sure Docker Desktop is installed and running
   - Check Windows services: Docker Desktop Service should be running
   - Restart Docker Desktop

2. **Port 6379 already in use**
   ```powershell
   # Find what's using the port
   netstat -ano | findstr :6379
   
   # Use different port
   docker run -d --name contentalchemy-redis -p 6380:6379 redis:7-alpine
   # Update REDIS_PORT=6380 in .env
   ```

3. **Connection timeout**
   - Check firewall settings
   - Verify Docker network is working
   - Try: `docker exec -it contentalchemy-redis redis-cli ping`

## Redis CLI Commands

```bash
# Connect to Redis CLI
docker exec -it contentalchemy-redis redis-cli

# Inside Redis CLI:
PING                    # Should return PONG
KEYS *                  # List all keys
GET key_name           # Get value
DEL key_name           # Delete key
FLUSHDB                # Clear all data
```
