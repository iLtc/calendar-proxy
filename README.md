# Calendar Proxy

// TODO: Add description

## Environment Variables

// TODO: Add environment variables

## Running Locally

1. Create a `.env` file with your environment variables
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Docker

### Pull from Docker Hub

```bash
docker pull iltc/calendar-proxy:latest
```

### Run the Container

```bash
docker run -p 8000:8000 \
  -e FEED_0_NAME="work" \
  -e FEED_0_SOURCE_0="https://calendar.example.com/work.ics" \
  -e FEED_0_TOKEN_0="your_secret_token" \
  iltc/calendar-proxy:latest
```

### Build Locally

```bash
docker build -t calendar-proxy:latest .
```

### Build Multi-Architecture Image (ARM64 + AMD64)

To build and push a multi-architecture image that works on both ARM (e.g., Apple Silicon, Raspberry Pi) and AMD64 (e.g., Intel/AMD servers):

```bash
# Build and push for both platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t iltc/calendar-proxy:latest \
  --push .
```

> **Note:** The `--push` flag is required for multi-platform builds because the resulting image is a manifest list that references platform-specific images stored in the registry.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check, returns `{"status": "ok"}` |
| `GET /{feed_name}/{token}.ics` | Returns the filtered calendar for the specified feed |

### Example

With this configuration:

```bash
FEED_0_NAME=work
FEED_0_SOURCE_0=https://calendar.example.com/work.ics
FEED_0_TOKEN_0=abc123
```

Access your filtered calendar at:

```
http://localhost:8000/work/abc123.ics
```

## License

MIT
