#!/bin/bash
# Database initialization script
# Run this to create all tables in the PostgreSQL database

set -e

echo "Installing dependencies..."
pip install -q psycopg2-binary

echo "Running database schema..."
python -c "
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Read and execute the schema
from db.database import get_connection

with open('db/schema.sql', 'r') as f:
    schema = f.read()

conn = get_connection()
with conn.cursor() as cursor:
    cursor.execute(schema)
conn.commit()
conn.close()

print('Database schema created successfully!')
"
