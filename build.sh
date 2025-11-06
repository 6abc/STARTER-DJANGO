#!/usr/bin/env bash
set -o errexit  # exit on error

echo "🚀 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --no-input

echo "🧩 Applying migrations..."
# Try DB-related commands but don't fail build if DB isn't ready
python manage.py makemigrations accounts || echo "⚠️ Skipping makemigrations (database not ready)"
python manage.py migrate accounts || echo "⚠️ Skipping migrate accounts (database not ready)"
python manage.py makemigrations || echo "⚠️ Skipping makemigrations (database not ready)"
python manage.py migrate || echo "⚠️ Skipping migrate (database not ready)"

echo "👑 Creating superuser (if possible)..."
python manage.py shell <<EOF || echo "⚠️ Could not create superuser (database not ready)"
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME:-admin}"
email = "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
password = "${DJANGO_SUPERUSER_PASSWORD:-admin123}"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

echo "✅ Build script completed successfully."
