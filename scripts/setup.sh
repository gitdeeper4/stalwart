#!/bin/bash
# STALWART - Main Setup Script
echo "🔧 Running STALWART setup..."

# استخدام bash مباشرة لتشغيل الملف
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/setup_database.sh"

echo "✅ Setup complete"
