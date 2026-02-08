#!/usr/bin/env python3
"""
Database initialization script.
Run this to create all tables in the PostgreSQL database.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import get_connection


def init_database():
    """Initialize the database with schema."""
    print("Reading schema...")
    with open('db/schema.sql', 'r') as f:
        schema = f.read()

    print("Connecting to database...")
    conn = get_connection()

    print("Creating tables...")
    with conn.cursor() as cursor:
        cursor.execute(schema)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def test_connection():
    """Test the database connection."""
    print("Testing database connection...")
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    conn.close()
    print(f"Connection successful! Result: {result}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_connection()
    else:
        init_database()
