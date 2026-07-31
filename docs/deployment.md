# Deployment

## Docker (recommended)

Docker bundles the exact Python version and dependencies the bot was built and tested with, so there's no environment drift between development and production.

```bash
# Build the image
docker build -t broryat-ai .

# Run it, loading configuration from .env
docker run -d \
  --name broryat-ai \
  --env-file .env \
  --restart unless-stopped \
  broryat-ai

# Follow logs
docker logs -f broryat-ai
```

To deploy new code, rebuild and replace the running container:

```bash
docker build -t broryat-ai .
docker stop broryat-ai && docker rm broryat-ai
docker run -d --name broryat-ai --env-file .env --restart unless-stopped broryat-ai
```

## Render

`render.yaml` defines a free-tier Docker web service. The bot uses Telegram long polling, so a lightweight health-check HTTP server runs alongside it purely to satisfy Render's requirement that a web service bind a port.

## CI/CD

GitHub Actions runs two checks for every pull request and every push to `main`:

- The complete test suite with Python 3.13 and the frozen `uv.lock`.
- A production Docker image build.

Render is configured with `autoDeployTrigger: checksPass`, so changes merged to
`main` deploy only after both checks succeed. Link the Render service to this
GitHub repository and apply `render.yaml`; no deployment secret is required.

> **Note:** Render's free tier spins down idle services. Pair the deployment with an uptime pinger (e.g. [UptimeRobot](https://uptimerobot.com)) if you need the bot to stay responsive at all times.
