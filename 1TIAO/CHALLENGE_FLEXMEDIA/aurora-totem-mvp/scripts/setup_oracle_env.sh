#!/bin/bash

# Aurora Totem - Oracle Environment Setup
# Fixes Oracle client library path issues on macOS

echo "🔧 Setting up Oracle environment for Aurora Totem..."

# Set Oracle client library paths
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export ORACLE_HOME="/opt/homebrew/lib"

# Verify Oracle libraries
if [ -f "/opt/homebrew/lib/libclntsh.dylib" ]; then
    echo "✅ Oracle client libraries found at: /opt/homebrew/lib"
else
    echo "❌ Oracle client libraries not found. Install with: brew install instantclient-arm64-basic"
    exit 1
fi

# Test Oracle connection
echo "🔍 Testing Oracle connection..."
python3 -c "
try:
    from database import DatabaseManager
    db = DatabaseManager()
    if db.connect():
        print('✅ Oracle FIAP connection: SUCCESS')
        stats = db.get_database_stats()
        print(f'📊 Database records: {stats.get(\"total_records\", 0)}')
        print(f'📋 Storage mode: {stats.get(\"storage_mode\", \"unknown\")}')
    else:
        print('❌ Oracle FIAP connection: FAILED')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo "🎉 Oracle environment setup complete!"