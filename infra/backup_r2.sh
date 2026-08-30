#!/bin/bash
# Hermes-Ecom automated Postgres backup to Cloudflare R2 (Free Tier).
# Requires AWS CLI or rclone configured with Cloudflare R2 S3-compatible credentials.
#
# Environment variables:
#   R2_BUCKET: Name of the Cloudflare R2 bucket (e.g. hermes-backups)
#   R2_ENDPOINT_URL: https://<account_id>.r2.cloudflarestorage.com
#   POSTGRES_USER, POSTGRES_DB (from .env)

set -euo pipefail

BACKUP_DIR="/tmp/hermes-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="medusa_db_${TIMESTAMP}.sql.gz"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting Postgres backup..."
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-medusa}" "${POSTGRES_DB:-medusa}" | gzip > "${FILEPATH}"

echo "[$(date)] Backup created at ${FILEPATH} ($(du -h "${FILEPATH}" | cut -f1))"

if [ -n "${R2_BUCKET:-}" ] && [ -n "${R2_ENDPOINT_URL:-}" ]; then
    echo "[$(date)] Uploading to Cloudflare R2 bucket: ${R2_BUCKET}..."
    aws s3 cp "${FILEPATH}" "s3://${R2_BUCKET}/${FILENAME}" --endpoint-url "${R2_ENDPOINT_URL}"
    echo "[$(date)] Successfully uploaded to Cloudflare R2."
else
    echo "[$(date)] R2_BUCKET or R2_ENDPOINT_URL not set — keeping local backup only."
fi

# Retain only last 7 days locally
find "${BACKUP_DIR}" -type f -name "medusa_db_*.sql.gz" -mtime +7 -delete
echo "[$(date)] Backup completed successfully."
