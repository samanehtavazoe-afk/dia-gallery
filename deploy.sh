#!/usr/bin/env bash
set -euo pipefail

DOMAIN="samaneh.filmjadiid.ir"
APP_DIR="/opt/dia-gallery"
BRANCH="dia"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: run with sudo/root"
    exit 1
fi

cd "$APP_DIR"

if [ "$(git branch --show-current)" != "$BRANCH" ]; then
    echo "ERROR: expected branch dia"
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: working tree is dirty"
    git status --short
    exit 1
fi

echo "=== UPDATE SOURCE ==="

git fetch origin "$BRANCH"
git merge --ff-only "origin/$BRANCH"

if ! command -v docker >/dev/null 2>&1; then
    echo "=== INSTALL DOCKER ==="

    apt-get update
    apt-get install -y ca-certificates curl openssl git

    install -m 0755 -d /etc/apt/keyrings

    . /etc/os-release

    curl -fsSL \
      "https://download.docker.com/linux/${ID}/gpg" \
      -o /etc/apt/keyrings/docker.asc

    chmod a+r /etc/apt/keyrings/docker.asc

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" \
      > /etc/apt/sources.list.d/docker.list

    apt-get update

    apt-get install -y \
      docker-ce \
      docker-ce-cli \
      containerd.io \
      docker-buildx-plugin \
      docker-compose-plugin
fi

if [ ! -f .env ]; then

    SECRET_KEY="$(openssl rand -hex 32)"
    DB_PASSWORD="$(openssl rand -hex 24)"
    ADMIN_PASSWORD="$(openssl rand -hex 16)"

    cat > .env <<ENV
DEBUG=0

SECRET_KEY=$SECRET_KEY

ALLOWED_HOSTS=$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN

DB_NAME=dia_gallery
DB_USER=dia_gallery
DB_PASSWORD=$DB_PASSWORD
DB_HOST=db
DB_PORT=5432

APP_ADMIN_USERNAME=diaadmin
APP_ADMIN_PASSWORD=$ADMIN_PASSWORD
ENV

    chmod 600 .env

    echo
    echo "========================================"
    echo "DIA ADMIN"
    echo "username: diaadmin"
    echo "password: $ADMIN_PASSWORD"
    echo "SAVE THIS PASSWORD"
    echo "========================================"
    echo
else
    echo "Existing .env preserved."
fi

echo "=== COMPOSE VALIDATION ==="

docker compose -p dia-gallery config >/dev/null

echo "=== BUILD / START ==="

docker compose -p dia-gallery up -d --build

echo
echo "=== SERVICES ==="

docker compose -p dia-gallery ps

echo
echo "=== DJANGO CHECK ==="

docker compose -p dia-gallery exec -T web \
    python manage.py check

echo
echo "=== DATA ISOLATION ==="

docker compose -p dia-gallery exec -T web \
    python manage.py shell -c \
'from dia_core.models import Product,SaleDay,StockBalance,Account; print({"products":Product.objects.count(),"sale_days":SaleDay.objects.count(),"stock_rows":StockBalance.objects.count(),"accounts":Account.objects.count()})'

echo
echo "=== VERSION ==="

git rev-parse HEAD

echo
echo "https://$DOMAIN"
echo
echo "SUCCESS: DIA GALLERY BASE DEPLOYED"
