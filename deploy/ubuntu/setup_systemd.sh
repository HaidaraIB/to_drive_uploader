#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   sudo bash deploy/ubuntu/setup_systemd.sh \
#     --project-dir /opt/to_drive_uploader \
#     --user botuser \
#     --group botuser \
#     --service-name to-drive-uploader

PROJECT_DIR=""
SERVICE_USER=""
SERVICE_GROUP=""
SERVICE_NAME="to-drive-uploader"
PYTHON_BIN="python3"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir)
      PROJECT_DIR="${2:-}"
      shift 2
      ;;
    --user)
      SERVICE_USER="${2:-}"
      shift 2
      ;;
    --group)
      SERVICE_GROUP="${2:-}"
      shift 2
      ;;
    --service-name)
      SERVICE_NAME="${2:-}"
      shift 2
      ;;
    --python)
      PYTHON_BIN="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$PROJECT_DIR" || -z "$SERVICE_USER" || -z "$SERVICE_GROUP" ]]; then
  echo "Missing required arguments." >&2
  echo "Required: --project-dir --user --group" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  echo "User does not exist: $SERVICE_USER" >&2
  exit 1
fi

cd "$PROJECT_DIR"

if [[ ! -f ".env" ]]; then
  echo ".env file not found in project root." >&2
  exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
  echo "requirements.txt file not found in project root." >&2
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

# Validate common credentials locations used in README/.env examples.
if [[ ! -f "credentials/credentials.json" ]]; then
  echo "Warning: credentials/credentials.json not found." >&2
fi
if [[ ! -f "credentials/refresh_token.txt" ]]; then
  echo "Warning: credentials/refresh_token.txt not found." >&2
fi

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
cp "$PROJECT_DIR/systemd/to-drive-uploader.service" "$SERVICE_FILE"
sed -i "s|__PROJECT_DIR__|$PROJECT_DIR|g" "$SERVICE_FILE"
sed -i "s|__SERVICE_USER__|$SERVICE_USER|g" "$SERVICE_FILE"
sed -i "s|__SERVICE_GROUP__|$SERVICE_GROUP|g" "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

echo "Service installed and started: ${SERVICE_NAME}.service"
echo "Status: systemctl status ${SERVICE_NAME}.service"
echo "Logs:   journalctl -u ${SERVICE_NAME}.service -f"
