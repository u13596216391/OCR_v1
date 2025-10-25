#!/bin/sh

# Minimal, ASCII-only entrypoint to avoid shell parsing issues on some images
# Wait for Postgres
/app/wait-for-it.sh "$POSTGRES_HOST:$POSTGRES_PORT"

# Wait for Redis
/app/wait-for-it.sh "$REDIS_HOST:6379"

# Execute the passed command
exec "$@"