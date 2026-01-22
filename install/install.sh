#!/usr/bin/env bash
set -e

APP_NAME="starter_django"
APP_USER="$USER"
BASE_DIR="/opt/$APP_NAME"
VENV_DIR="$BASE_DIR/venv"
PROJECT_DIR="$BASE_DIR/project"
DOMAIN="localhost"

PYTHON_BIN="python3.10"

LOG="install_$(date +%Y%m%d_%H%M).log"

exec > >(tee -i $LOG)
exec 2>&1

print() {
    echo -e "\n==== $1 ====\n"
}

error() {
    echo "❌ ERROR: $1"
    exit 1
}

print "Starting $APP_NAME installation"

# -------------------------------
# Root check
# -------------------------------
if [ "$EUID" -ne 0 ]; then
    error "Run as root: sudo ./install.sh"
fi

# -------------------------------
# System packages
# -------------------------------
print "Installing system packages"

apt update
apt install -y \
    python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx curl build-essential libpq-dev

# -------------------------------
# Create folders
# -------------------------------
print "Creating directories"

mkdir -p $PROJECT_DIR
cp -r ../* $PROJECT_DIR

# -------------------------------
# Python venv
# -------------------------------
print "Creating virtualenv"

python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

pip install --upgrade pip
pip install -r $PROJECT_DIR/requirements.txt
pip install gunicorn psycopg2-binary

# -------------------------------
# PostgreSQL setup
# -------------------------------
print "Configuring PostgreSQL"

DB_NAME="${APP_NAME}_db"
DB_USER="${APP_NAME}_user"
DB_PASS=$(openssl rand -hex 16)

sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# -------------------------------
# Env file
# -------------------------------
print "Creating environment file"

cat > $PROJECT_DIR/.env <<EOF
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=$DOMAIN

DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_HOST=localhost
DB_PORT=5432
EOF

chown -R $APP_USER:$APP_USER $BASE_DIR

# -------------------------------
# Django setup
# -------------------------------
print "Running migrations"

cd $PROJECT_DIR
source $VENV_DIR/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput

# -------------------------------
# Gunicorn systemd
# -------------------------------
print "Installing gunicorn service"

sed "s|__APP_NAME__|$APP_NAME|g; s|__APP_USER__|$APP_USER|g; s|__BASE_DIR__|$BASE_DIR|g" gunicorn.service > /etc/systemd/system/$APP_NAME.service

systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME

# -------------------------------
# Nginx
# -------------------------------
print "Installing nginx config"

sed "s|__DOMAIN__|$DOMAIN|g; s|__APP_NAME__|$APP_NAME|g; s|__BASE_DIR__|$BASE_DIR|g" nginx.conf > /etc/nginx/sites-available/$APP_NAME

ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/

nginx -t
systemctl restart nginx

print "Installation complete!"
print "App running at: http://$DOMAIN"
print "Log file: $LOG"
